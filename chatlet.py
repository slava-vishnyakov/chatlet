import requests
import json
import re
from typing import List, Dict, Union, Optional, Callable
import base64
import os
import inspect
from dotenv import load_dotenv
from .model_pricing import get_model_pricing
from fastcore.docments import docments

class ChatletError(Exception):
    pass

class MetaChatlet(type):
    _default_model = "anthropic/claude-3.5-sonnet"
    _total_usd_sum = 0.0

    @property
    def DEFAULT_MODEL(cls):
        return cls._default_model

    @DEFAULT_MODEL.setter
    def DEFAULT_MODEL(cls, value):
        cls._default_model = value

    @property
    def total_usd_sum(cls):
        return cls._total_usd_sum

    @total_usd_sum.setter
    def total_usd_sum(cls, value):
        cls._total_usd_sum = value


class Chatlet(metaclass=MetaChatlet):

    _cancel_streaming: bool = False

    def __init__(self, model: str = None, system_prompt: str = None,
                 http_referer: str = None, x_title: str = None, api_key: str = None):
        self.model = model if model else __class__.DEFAULT_MODEL
        self.debug = False
        self.system_prompt = system_prompt
        self.api_key = api_key if api_key else self._get_api_key()
        self.base_url = "https://openrouter.ai/api/v1"
        self.conversation_history = []
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.image_count = 0
        self.total_usd = 0
        self.last_request_usd = 0
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if http_referer:
            self.headers["HTTP-Referer"] = http_referer
        if x_title:
            self.headers["X-Title"] = x_title

    def get_rate_limits_and_credits(self):
        response = requests.get(f"{self.base_url}/auth/key", headers=self.headers)
        if response.status_code != 200:
            raise ChatletError(f"API request failed with status code {response.status_code}: {response.text}")
        return response.json()

    def get_token_limits(self):
        response = requests.get(f"{self.base_url}/models", headers=self.headers)
        if response.status_code != 200:
            raise ChatletError(f"API request failed with status code {response.status_code}: {response.text}")
        return response.json()

    def _get_api_key(self):
        load_dotenv()
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ChatletError("OPENROUTER_API_KEY not found in .env file or not provided as a parameter")
        return api_key

    def _create_tool(self, func: Callable):
        doc = docments(func, full=True)
        tool = {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__.strip() if func.__doc__ else "",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
        
        for param_name, param_info in doc.items():
            if param_name != 'return':
                param_type = self._get_json_schema_type(param_info.anno)
                tool['function']['parameters']['properties'][param_name] = {
                    "type": param_type,
                    "description": param_info.docment or ""
                }
                if param_info.default == inspect._empty:
                    tool['function']['parameters']['required'].append(param_name)
        
        if 'return' in doc:
            tool['function']['returns'] = {
                "type": self._get_json_schema_type(doc['return'].anno),
                "description": doc['return'].docment
            }
        
        return tool

    def _get_json_schema_type(self, anno):
        if anno == inspect._empty:
            return "string"
        elif anno == str:
            return "string"
        elif anno == int:
            return "integer"
        elif anno == float:
            return "number"
        elif anno == bool:
            return "boolean"
        elif anno == dict:
            return "object"
        elif anno == list:
            return "array"
        else:
            return "string"  # Default to string for unknown types

    def add_user(self, content: str):
        self.conversation_history.append({"role": "user", "content": content})

    def add_assistant(self, content: str):
        self.conversation_history.append({"role": "assistant", "content": content})

    def add_tool_use(self, tool_name: str, arguments: dict, result: any):
        tool_description = f"Tool '{tool_name}' was called with arguments: {arguments}. It returned: {result}"
        self.conversation_history.append({"role": "function", "name": tool_name, "content": tool_description})

    def _prepare_messages(self):
        messages = self.conversation_history.copy()
        if self.system_prompt:
            messages.insert(0, {"role": "system", "content": self.system_prompt})
        
        # Change "function" roles to "assistant" for API compatibility
        for message in messages:
            if message["role"] == "function":
                message["role"] = "assistant"
        
        return messages

    def __call__(self, message: str, **kwargs):
        self.add_user(message)
        messages = self._prepare_messages()

        payload = {
            "model": self.model,
            "messages": messages,
        }

        # Handle optional parameters
        if kwargs.get('require_json'):
            payload["response_format"] = {"type": "json_object"}
        for param in ['temperature', 'max_tokens', 'stop', 'stream', 'tool_choice']:
            if param == 'tool_choice' and kwargs.get(param) is not None:
                payload[param] = {'type': 'function', 'function': {'name': kwargs[param]}}
            elif param in kwargs:
                payload[param] = kwargs[param]
        if 'images' in kwargs:
            payload['messages'][-1]['content'] = self._prepare_image_content(message, kwargs['images'])
        if 'urls' in kwargs:
            payload['messages'][-1]['content'] += "\n\n" + self._fetch_url_contents(kwargs['urls'])
        if 'tools' in kwargs:
            payload['tools'] = [self._create_tool(func) for func in kwargs['tools']]
        # Valid providers: OpenAI, Anthropic, HuggingFace, Google, Together, DeepInfra, Azure, Modal, AnyScale,
        # Replicate, Perplexity, Recursal, Fireworks, Mistral, Groq, Cohere, Lepton, OctoAI, Novita, DeepSeek,
        # Infermatic, AI21, Featherless, Mancer, Mancer 2, Lynn 2, Lynn
        if 'provider_order' in kwargs or 'provider_allow_fallbacks' in kwargs:
            payload['provider'] = {}
            if 'provider_order' in kwargs:
                payload['provider']['order'] = kwargs['provider_order']
            if 'provider_allow_fallbacks' in kwargs:
                payload['provider']['allow_fallbacks'] = kwargs['provider_allow_fallbacks']

        is_stream = kwargs.get('stream', False)
        if self.debug:
            print(f"Sending request to OpenRouter API [stream={is_stream}]: {payload}\n----------------")
        response = requests.post(f"{self.base_url}/chat/completions", headers=self.headers, json=payload, stream=is_stream)
        if self.debug:
            if is_stream:
                print(f"Receiving stream from OpenRouter API...\n----------------")
            else:
                print(f"Received response from OpenRouter API: {response.text}\n----------------")

        if response.status_code == 502:
            raise ChatletError("OpenRouter API is currently unavailable. Please try again later.")

        if response.status_code != 200:
            raise ChatletError(f"API request failed with status code {response.status_code}: {response.text}")

        if is_stream:
            return self._handle_streaming(response)
        else:
            data = response.json()
            if 'error' in data and 'message' in data['error'] and data['error']['message'].startswith('{'):
                inner_error = json.loads(data['error']['message'])['error']
                # print(inner_error)
                # inner_error = {'type': 'invalid_request_error', 'message': 'tools.0.input_schema: JSON schema is invalid - please consult https://json-schema.org or our documentation at https://docs.anthropic.com/en/docs/tool-use'}
                for i in range(len(payload['tools'])):
                    if 'message' in inner_error and inner_error['message'].startswith(f'tools.{i}.input_schema: JSON schema is invalid'):
                        schema = payload['tools'][i]['function']
                        raise ChatletError(f"Incorrect schema for tool {schema['name']}: {schema['parameters']['properties']}")


                raise ChatletError(f"API request failed with error: {data['error']}")
            self._update_token_count(data['usage'])
            message = data['choices'][0]['message']
            content = message['content']

            self.tool_called = None
            self.tool_args = None
            self.tool_result = None
            if 'tool_calls' in message:
                self._handle_tool_calls(message['tool_calls'], kwargs.get('tools', []))

            if kwargs.get('require_json'):
                # Extract JSON content from the response
                json_content = self._extract_json(content)
                return json.loads(json_content)
            else:
                return content

    def _extract_json(self, content: str) -> str:
        # Find JSON content between triple backticks
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
        if json_match:
            return json_match.group(1)
        
        # If no JSON block found, try to find content between curly braces
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json_match.group(0)
        
        # If still no JSON found, return the original content
        return content

    def _handle_tool_calls(self, tool_calls, available_tools):
        for tool_call in tool_calls:
            if tool_call['type'] == 'function':
                function = tool_call['function']
                self.tool_called = function['name']
                self.tool_args = json.loads(function['arguments'])
                
                tool_func = next((func for func in available_tools if func.__name__ == self.tool_called), None)
                if tool_func:
                    self.tool_result = tool_func(**self.tool_args)
                else:
                    self.tool_result = None
                    print(f"Warning: Tool '{self.tool_called}' was called but not found in the provided tools.")

                self.add_tool_use(self.tool_called, self.tool_args, self.tool_result)

    def _prepare_image_content(self, message: str, image_files: List[str]) -> List[Dict]:
        content = [{"type": "text", "text": message}]
        self.image_count = 0  # Reset image count for this request
        for image_file in image_files:
            with open(image_file, "rb") as img:
                base64_image = base64.b64encode(img.read()).decode('utf-8')
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                })
            self.image_count += 1  # Increment image count
        return content

    def _fetch_url_contents(self, urls: List[str]) -> str:
        contents = []
        for url in urls:
            response = requests.get(url)
            if response.status_code == 200:
                contents.append(f"Content from {url}:\n\n{response.text}")
            else:
                contents.append(f"Failed to fetch content from {url}")
        return "\n\n".join(contents)

    def _update_token_count(self, usage: Dict[str, int]):
        self.prompt_tokens += usage['prompt_tokens']
        self.completion_tokens += usage['completion_tokens']
        self.total_tokens += usage['total_tokens']
        self._estimate_price()

    def _estimate_price(self):
        pricing = get_model_pricing(self.model)
        # print(pricing, self.model)

        input_cost = self.prompt_tokens * pricing['input_price_per_token']
        output_cost = self.completion_tokens * pricing['output_price_per_token']
        
        image_cost = (self.image_count / 1000) * pricing['image_price_per_thousand'] if hasattr(self, 'image_count') else 0

        self.last_request_usd = input_cost + output_cost + image_cost
        self.total_usd += self.last_request_usd

        __class__.total_usd_sum += self.last_request_usd

    def _handle_streaming(self, response):
        self._cancel_streaming = False
        for line in response.iter_lines():
            if self._cancel_streaming:
                break
            line = line.decode('utf-8')
            if line.startswith('data: '):
                try:
                    data = json.loads(line.split('data: ')[1])
                    yield data['choices'][0]['delta'].get('content', '')
                except json.JSONDecodeError:
                    continue
            elif line == ': OPENROUTER PROCESSING' or line == '':
                continue
            else:
                raise ChatletError(f"Unexpected response from OpenRouter API: {line}")

    def cancel(self):
        self._cancel_streaming = True
