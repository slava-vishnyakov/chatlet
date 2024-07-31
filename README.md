# Chatette

Chatette is a powerful and flexible chatbot framework designed to work seamlessly with OpenRouter, supporting a wide
range of models. Inspired by [Claudette](https://claudette.answer.ai/), Chatette aims to provide an easy-to-use
interface for building and managing conversational AI applications.

## Why Chatette?

While Claudette is a great tool, it is specifically tailored for a particular use case (Anthropic's Claude). Chatette, on the other hand, is
designed to be more versatile and can work with any model supported by OpenRouter. 

## Features

- **Model Agnostic**: Supports any model available on OpenRouter.
- **Easy Integration**: Simple API for integrating with your applications.
- **Cost Estimation**: Built-in cost estimation for API usage for some popular models.

## Getting Started

### Installation

To install Chatette, simply clone the repository and install the dependencies:

```bash
git clone https://github.com/yourusername/chatette.git
cd chatette
pip install -r requirements.txt
```

### Basic Usage

Here's a simple example to get you started:

```python
from chatette import Chatette

# Initialize Chatette with the desired model
chat = Chatette() 
```

This loads API key from OPENROUTER_API_KEY environment variable or .env file.
The default model is `anthropic/claude-3.5-sonnet`.

Or, if you want to provide the model and API key directly:

```python
chat = Chatette(model="anthropic/claude-3.5-sonnet", api_key="your_api_key_here")
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
        "content": "My name is Chatette."
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
chat("What's the weather like in New York City?", tools=[get_weather], tool_choice="get_weather")
```

You can customize the behavior of Chatette by passing additional parameters:

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

Here are some important examples of how to use Chatette:

### Basic Usage

```python
from chatette import Chatette

chat = Chatette()
response = chat("Hello, how are you?")
print(response)
```

### Custom Model

```python
custom_chat = Chatette(model="openai/gpt-3.5-turbo")
response = custom_chat("Tell me a joke")
print(response)
```

### System Prompt

```python
system_prompt = "You are a helpful assistant named Claude. Your favorite color is blue."
chat = Chatette(system_prompt=system_prompt)
response = chat("What's your name and favorite color?")
print(response)
```

### Streaming Response

```python
chat = Chatette()
stream = chat("Tell me a story in 10 words.", stream=True)
for chunk in stream:
    print(chunk, end='', flush=True)
print()  # New line after streaming
```

### Image Input

```python
chat = Chatette()
response = chat("What's in this image?", images=["path/to/image.jpg"])
print(response)
```

### Using Tools

```python
def get_weather(location: str, unit: str = "celsius") -> dict:
    """Get the current weather in a given location."""
    return {"temperature": 22, "unit": unit, "condition": "Sunny"}

chat = Chatette()
response = chat("What's the weather like in New York City?", tools=[get_weather])
print(response)
print(f"Tool called: {chat.tool_called}")
print(f"Tool arguments: {chat.tool_args}")
print(f"Tool result: {chat.tool_result}")
```

### Cost Estimation

```python
chat = Chatette()
response = chat("Hello, how are you?")
print(f'Estimated cost: ${chat.total_usd:.6f}, last request: ${chat.last_request_usd:.6f}')
```

### Custom Headers

```python
chat = Chatette(http_referer="https://myapp.com", x_title="My Cool App")
response = chat("Hello")
print(response)
```

### Requiring JSON Output

```python
chat = Chatette()
response = chat("List three colors in JSON format", require_json=True)
print(response)  # This will be a Python dictionary
```

### URL Context

```python
chat = Chatette()
response = chat("Summarize the article I provided", urls=["https://example.com/article"])
print(response)
```

### Temperature and Max Tokens

```python
chat = Chatette()
response = chat("Tell me a story", temperature=0.7, max_tokens=100)
print(response)
```

### Adding Conversation History

```python
chat = Chatette()
chat.add_user("What's the capital of France?")
chat.add_assistant("The capital of France is Paris.")
chat.add_user("What's its population?")
response = chat("Summarize our conversation.")
print(response)
```

### Specifying Provider Order and Fallbacks

```python
chat = Chatette()
response = chat("Hello", provider_order=["OpenAI", "Anthropic"], provider_allow_fallbacks=False)
print(response)
```

### Available Providers

Chatette supports a wide range of AI providers through OpenRouter. As of the last update, the available providers include:

1. OpenAI
2. Anthropic
3. HuggingFace
4. Google
5. Together
6. DeepInfra
7. Azure
8. Modal
9. AnyScale
10. Replicate
11. Perplexity
12. Recursal
13. Fireworks
14. Mistral
15. Groq
16. Cohere
17. Lepton
18. OctoAI
19. Novita
20. DeepSeek
21. Infermatic
22. AI21
23. Featherless
24. Mancer
25. Mancer 2
26. Lynn 2
27. Lynn

Please note that the availability of providers may change over time. For the most up-to-date list, refer to the OpenRouter documentation.

These examples showcase the versatility and power of Chatette. For more detailed information on each feature, please
refer to the API Reference section.

## API Reference

### Chatette Class

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
# Chatette

Chatette is a Python wrapper for the OpenRouter API, providing an easy-to-use interface for interacting with various AI models.

## Installation

You can install Chatette using pip:

```
pip install chatette
```

## Usage

Here's a quick example of how to use Chatette:

```python
from chatette import Chatette

# Initialize the Chatette client
chat = Chatette(api_key="your_api_key_here")

# Send a message and get a response
response = chat("Hello, how are you?")
print(response)
```

## Features

- Easy-to-use interface for the OpenRouter API
- Support for multiple AI models
- Streaming responses
- Tool usage
- Image input support
- Conversation history management

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
