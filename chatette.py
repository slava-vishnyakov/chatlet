import requests
import json
from typing import List, Dict, Union, Optional, Callable
import base64
import os
from dotenv import load_dotenv
from model_pricing import get_model_pricing

class ChatetteError(Exception):
    pass

class Chatette:
    _cancel_streaming: bool = False

    def __init__(self, model: str = "anthropic/claude-3-opus", system_prompt: str = None,
                 http_referer: str = None, x_title: str = None):
        self.model = model
        self.system_prompt = system_prompt
        self.api_key = self._get_api_key()
        self.base_url = "https://openrouter.ai/api/v1"
        self.conversation_history = []
        self.tools = []
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

    def _get_api_key(self):        
        load_dotenv()
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ChatetteError("OPENROUTER_API_KEY not found in .env file")
        return api_key

    def add_tool(self, func: Callable):
        tool = {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
        # Parse the function's type hints and docstring to populate the parameters
        # This is a simplified version and might need to be more robust in a real implementation
        for param_name, param_type in func.__annotations__.items():
            if param_name != 'return':
                tool['function']['parameters']['properties'][param_name] = {"type": param_type.__name__}
                tool['function']['parameters']['required'].append(param_name)
        
        self.tools.append(tool)

    def addUser(self, content: str):
        self.conversation_history.append({"role": "user", "content": content})

    def addAssistant(self, content: str):
        self.conversation_history.append({"role": "assistant", "content": content})

    def __call__(self, message: str, **kwargs):
        messages = self.conversation_history.copy()
        if self.system_prompt:
            messages.insert(0, {"role": "system", "content": self.system_prompt})
        self.addUser(message)
        messages = self.conversation_history.copy()

        payload = {
            "model": self.model,
            "messages": messages,
        }

        # Handle optional parameters
        if kwargs.get('require_json'):
            payload["response_format"] = {"type": "json_object"}
        for param in ['temperature', 'max_tokens', 'stop', 'stream', 'tool_choice']:
            if param in kwargs:
                payload[param] = kwargs[param]
        if 'images' in kwargs:
            payload['messages'][-1]['content'] = self._prepare_image_content(message, kwargs['images'])
        if 'urls' in kwargs:
            payload['messages'][-1]['content'] += "\n\n" + self._fetch_url_contents(kwargs['urls'])
        if self.tools:
            payload['tools'] = self.tools
        if 'provider_preferences' in kwargs:
            payload['provider'] = kwargs['provider_preferences']

        response = requests.post(f"{self.base_url}/chat/completions", headers=self.headers, json=payload, stream=kwargs.get('stream', False))
        
        if response.status_code != 200:
            raise ChatetteError(f"API request failed with status code {response.status_code}: {response.text}")

        if kwargs.get('stream', False):
            return self._handle_streaming(response)
        else:
            data = response.json()
            # possible error here: {'error': {'message': '{"type":"error","error":{"type":"invalid_request_error","message":"messages.0.content.1.image.source.base64.data: The image was specified using the image/jpeg media type, but does not appear to be a valid jpeg image"}}
            if 'error' in data:
                raise ChatetteError(f"API request failed with error: {data['error']}")
            self._update_token_count(data['usage'])
            content = data['choices'][0]['message']['content']
            return json.loads(content) if kwargs.get('require_json') else content

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

        input_cost = self.prompt_tokens * pricing['input_price_per_token']
        output_cost = self.completion_tokens * pricing['output_price_per_token']
        
        image_cost = (self.image_count / 1000) * pricing['image_price_per_thousand'] if hasattr(self, 'image_count') else 0

        self.last_request_usd = input_cost + output_cost + image_cost
        self.total_usd += self.last_request_usd

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
                raise ChatetteError(f"Unexpected response from OpenRouter API: {line}")

    def cancel(self):
        self._cancel_streaming = True
