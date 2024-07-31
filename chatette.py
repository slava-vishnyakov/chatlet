import requests
import json
from typing import List, Dict, Union, Optional, Callable
import base64
import os
from dotenv import load_dotenv

class ChatetteError(Exception):
    pass

class Chatette:
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

        response = requests.post(f"{self.base_url}/chat/completions", headers=self.headers, json=payload)
        
        if response.status_code != 200:
            raise ChatetteError(f"API request failed with status code {response.status_code}: {response.text}")

        data = response.json()
        self._update_token_count(data['usage'])
        
        if kwargs.get('stream', False):
            return self._handle_streaming(response)
        else:
            content = data['choices'][0]['message']['content']
            return json.loads(content) if kwargs.get('require_json') else content

    def _prepare_image_content(self, message: str, image_files: List[str]) -> List[Dict]:
        content = [{"type": "text", "text": message}]
        for image_file in image_files:
            with open(image_file, "rb") as img:
                base64_image = base64.b64encode(img.read()).decode('utf-8')
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                })
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

    def _handle_streaming(self, response):
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8').split('data: ')[1])
                    yield data['choices'][0]['delta'].get('content', '')
                except json.JSONDecodeError:
                    continue

    def cancel(self):
        # This method should be called from another thread to cancel an ongoing streaming request
        # In a real implementation, you'd use something like requests.Session() to manage connections
        pass
