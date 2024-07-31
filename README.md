# Chatlet

Chatlet is a Python wrapper for the OpenRouter API, providing an easy-to-use interface for interacting with various AI models.
Inspired by [Claudette](https://claudette.answer.ai/), which supports only Anthropic Claude.

## Usage

Here's a quick example of how to use Chatlet:

```python
from chatlet import Chatlet

chat = Chatlet(api_key="Your-OpenRouter-API-key")
# loads claude-3.5-sonnet by default

chat("Hello, how are you?")
# I'm doing well, thank you!

chat('What\'s your name?')
# My name is Claude.
```

## Features

- Easy-to-use interface for the OpenRouter API
- Support for multiple AI models
- [Streaming responses](#streaming-response)
- [Tool usage](#using-tools)
- [Image input support](#image-input)
- [Adding URLs to context](#url-context)
- [Conversation history management](#adding-conversation-history)
- [Cost estimation](#cost-estimation)

## Why Chatlet?

Chatlet is designed to be versatile and can work with any model supported by OpenRouter.

## Getting Started

### Installation

To install Chatlet, simply clone the repository and install the dependencies:

```bash
git clone https://github.com/slava-vishnyakov/chatlet.git
cd chatlet
pip install -r requirements.txt
```

### Basic Usage

Here's a simple example to get you started:

```python
from chatlet import Chatlet
chat = Chatlet() 
```

This loads API key from `OPENROUTER_API_KEY` environment variable or .env file.
The default model is `anthropic/claude-3.5-sonnet`.

Or, if you want to provide the model and API key directly:

```python
chat = Chatlet(model="anthropic/claude-3.5-sonnet", api_key="your_api_key_here")
```

You can then send a message to the chatbot:

```python
response = chat("Hello, how are you?")
print(response)
```

> `I'm doing well, thank you! How can I assist you today?`

You can then continue the chat by calling the `chat` function again with a new message:

```python
response = chat("What's your name?")
print(response)
```

> `My name is Claude.`

All history is stored:

```python
chat.conversation_history
```

```json
[
    {
        "role": "user",
        "content": "Hello, how are you?"
    },
    {
        "role": "assistant",
        "content": "I'm doing great, thank you!"
    },
    {
        "role": "user",
        "content": "What's your name?"
    },
    {
        "role": "assistant",
        "content": "My name is Claude."
    }
]
```

You can also add images:

```python
chat("What's in this image?", images=["path/to/image.jpg"])
```

Or add tools using [docments](https://fastcore.fast.ai/docments.html#docments) (note the comments, this is `docments`, they will be sent to the model):

```python
def get_weather(
        location: str, # The location to get the weather for.
        unit: str = "celsius" # The unit to return the temperature in.
    ) -> dict: # Get the current weather in a given location.
    return {"temperature": 22, "unit": unit, "condition": "Sunny"}

chat("What's the weather like in New York City?", tools=[get_weather])
```

Force a specific tool using `tool_choice`:

```python
chat("What's the weather like in New York City?", 
     tools=[get_weather], 
     tool_choice="get_weather")
```

You can customize the behavior of Chatlet by passing additional parameters:

```python
response = chat("Tell me a story", temperature=0.7, max_tokens=100)
print(response)
```

Some other parameters you can use: `stream`, `images`, `urls`, `require_json`, `provider_order`, 
`provider_allow_fallbacks`.

Streaming example:

```python
stream = chat("Tell me a story in 10 words.", stream=True)
for chunk in stream:
    print(chunk, end='', flush=True)
    # call `chat.cancel()` at any time to stop the streaming request
```

And add some URLs:

```python
chat("Summarize the article I provided", urls=["https://example.com/article"])
```

## Examples

Here are some important examples of how to use Chatlet:

### Basic Usage

```python
from Chatlet import Chatlet

chat = Chatlet()
response = chat("Hello, how are you?")
print(response)
```

### Custom Model

```python
custom_chat = Chatlet(model="openai/gpt-3.5-turbo")
response = custom_chat("Tell me a joke")
print(response)
```

### System Prompt

```python
system_prompt = "You are a helpful assistant named Claude. Your favorite color is blue."
chat = Chatlet(system_prompt=system_prompt)
response = chat("What's your name and favorite color?")
print(response)
```

### Streaming Response

```python
chat = Chatlet()
stream = chat("Tell me a story in 10 words.", stream=True)
for chunk in stream:
    print(chunk, end='', flush=True)
print()  # New line after streaming
```

### Image Input

```python
chat = Chatlet()
response = chat("What's in this image?", images=["path/to/image.jpg"])
print(response)
```

### Using Tools

```python
def get_weather(location: str, unit: str = "celsius") -> dict:
    """Get the current weather in a given location."""
    return {"temperature": 22, "unit": unit, "condition": "Sunny"}

chat = Chatlet()
response = chat("What's the weather like in New York City?", tools=[get_weather])
print(response)
print(f"Tool called: {chat.tool_called}")
print(f"Tool arguments: {chat.tool_args}")
print(f"Tool result: {chat.tool_result}")
```

### Cost Estimation

```python
chat = Chatlet()
response = chat("Hello, how are you?")
print(f'Estimated cost: ${chat.total_usd:.6f}, last request: ${chat.last_request_usd:.6f}')
```

### Custom Headers

```python
chat = Chatlet(http_referer="https://myapp.com", x_title="My Cool App")
response = chat("Hello")
print(response)
```

### Requiring JSON Output

```python
chat = Chatlet()
response = chat("List three colors in JSON format", require_json=True)
print(response)  # This will be a Python dictionary
```

### URL Context

```python
chat = Chatlet()
response = chat("Summarize the article I provided", urls=["https://example.com/article"])
print(response)
```

### Temperature and Max Tokens

```python
chat = Chatlet()
response = chat("Tell me a story", temperature=0.7, max_tokens=100)
print(response)
```

### Adding Conversation History

```python
chat = Chatlet()
chat.add_user("What's the capital of France?")
chat.add_assistant("The capital of France is Paris.")
chat.add_user("What's its population?")
response = chat("Summarize our conversation.")
print(response)
```

### Specifying Provider Order and Fallbacks

```python
chat = Chatlet()
response = chat("Hello",
                model="meta-llama/llama-3.1-8b-instruct",
                provider_order=["DeepInfra", "Lepton", "Together"],
                provider_allow_fallbacks=False
                )
print(response)
```

### Available Providers

As of the last update, the available providers include:

`OpenAI`, `Anthropic`, `HuggingFace`, `Google`, `Together`, `DeepInfra`, `Azure`, `Modal`, `AnyScale`, 
`Replicate`, `Perplexity`, `Recursal`, `Fireworks`, `Mistral`, `Groq`, `Cohere`, `Lepton`, `OctoAI`, 
`Novita`, `DeepSeek`, `Infermatic`, `AI21`, `Featherless`, `Mancer`, `Mancer 2`, `Lynn 2`, `Lynn`

Please note that the availability of providers may change over time. For the most up-to-date list, refer to the OpenRouter documentation.

## API Reference

### Chatlet Class

#### `__init__(self, model: str = "anthropic/claude-3.5-sonnet", system_prompt: str = None, http_referer: str = None, x_title: str = None, api_key: str = None)`

- **model**: The model to use for the chatbot.
- **system_prompt**: An optional system prompt to set the context for the conversation.
- **http_referer**: Optional HTTP referer header.
- **x_title**: Optional X-Title header.
- **api_key**: Optional API key. If not provided, it will be loaded from the environment variable or .env file.

#### `__call__(self, message: str, **kwargs)`

- **message**: The message to send to the chatbot.
- **kwargs**: Additional parameters to customize the request. These can include:
  - **stream**: Boolean to enable streaming responses.
  - **temperature**: Float to control randomness in the response.
  - **max_tokens**: Integer to limit the response length.
  - **tools**: List of function objects to be used as tools.
  - **tool_choice**: String to specify which tool to use.
  - **images**: List of image file paths to include in the message.
  - **urls**: List of URLs to fetch content from.
  - **require_json**: Boolean to request JSON output.
  - **provider_order**: List of provider names to specify the order of providers to try.
  - **provider_allow_fallbacks**: Boolean to allow fallbacks to other providers.

#### `get_rate_limits_and_credits(self)`

Fetches the rate limits and credits for the API key.

#### `get_token_limits(self)`

Fetches the token limits for the available models.

#### `add_user(self, content: str)`

Adds a user message to the conversation history.

#### `add_assistant(self, content: str)`

Adds an assistant message to the conversation history.

#### `add_tool_use(self, tool_name: str, arguments: dict, result: any)`

Adds a tool usage entry to the conversation history.

#### `cancel(self)`

Cancels an ongoing streaming request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

Special thanks to the creators of [Claudette](https://claudette.answer.ai/) for the inspiration.
