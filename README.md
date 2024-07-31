# Chatette

Chatette is a powerful and flexible chatbot framework designed to work seamlessly with OpenRouter, supporting a wide
range of models. Inspired by [Claudette](https://claudette.answer.ai/), Chatette aims to provide an easy-to-use
interface for building and managing conversational AI applications.

## Why Chatette?

While Claudette is a great tool, it is specifically tailored for a particular use case. Chatette, on the other hand, is
designed to be more versatile and can work with any model supported by OpenRouter. This makes it an ideal choice for
developers looking for flexibility and ease of integration.

## Features

- **Model Agnostic**: Supports any model available on OpenRouter.
- **Easy Integration**: Simple API for integrating with your applications.
- **Extensible**: Easily add custom tools and functionalities.
- **Cost Estimation**: Built-in cost estimation for API usage.

## Getting Started

### Installation

To install Chatette, simply clone the repository and install the dependencies:

```bash
git clone https://github.com/yourusername/chatette.git
cd chatette
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory of your project and add your OpenRouter API key:

```
OPENROUTER_API_KEY=your_api_key_here
```

### Basic Usage

Here's a simple example to get you started:

```python
from chatette import Chatette

# Initialize Chatette with the desired model
chat = Chatette(model="anthropic/claude-3.5-sonnet")

# Send a message to the chatbot
response = chat("Hello, how are you?")
print(response)
```

### Advanced Usage

You can customize the behavior of Chatette by passing additional parameters:

```python
response = chat("Tell me a story", temperature=0.7, max_tokens=100)
print(response)
```

## API Reference

### Chatette Class

#### `__init__(self, model: str = "anthropic/claude-3.5-sonnet", system_prompt: str = None, http_referer: str = None, x_title: str = None)`

- **model**: The model to use for the chatbot.
- **system_prompt**: An optional system prompt to set the context for the conversation.
- **http_referer**: Optional HTTP referer header.
- **x_title**: Optional X-Title header.

#### `__call__(self, message: str, **kwargs)`

- **message**: The message to send to the chatbot.
- **kwargs**: Additional parameters to customize the request.

#### `get_rate_limits_and_credits(self)`

Fetches the rate limits and credits for the API key.

#### `get_token_limits(self)`

Fetches the token limits for the available models.

#### `addUser(self, content: str)`

Adds a user message to the conversation history.

#### `addAssistant(self, content: str)`

Adds an assistant message to the conversation history.

#### `addToolUse(self, tool_name: str, arguments: dict, result: any)`

Adds a tool usage entry to the conversation history.

#### `cancel(self)`

Cancels an ongoing streaming request.

## Contributing

We welcome contributions! Please read our [contributing guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Examples

Here are some important examples of how to use Chatette based on our test suite:

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
chat.addUser("What's the capital of France?")
chat.addAssistant("The capital of France is Paris.")
chat.addUser("What's its population?")
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
3. Google
4. Meta
5. Mistral AI
6. Cohere
7. AI21
8. Anyscale
9. Perplexity AI
10. Replicate
11. OpenRouter

Please note that the availability of providers may change over time. For the most up-to-date list, refer to the OpenRouter documentation.

These examples showcase the versatility and power of Chatette. For more detailed information on each feature, please
refer to the API Reference section.

## Acknowledgements

Special thanks to the creators of [Claudette](https://claudette.answer.ai/) for the inspiration.
