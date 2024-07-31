import pytest
import responses
from chatette import Chatette, ChatetteError
import base64
import json

def test_init():
    chat = Chatette()
    assert chat.model == "anthropic/claude-3-opus"
    
    custom_chat = Chatette(model="openai/gpt-3.5-turbo")
    assert custom_chat.model == "openai/gpt-3.5-turbo"

def test_send_message():
    chat = Chatette()
    response = chat("Hello, how are you?")
    assert isinstance(response, str)
    assert len(response) > 0

def test_system_prompt():
    chat = Chatette(system_prompt="You are a helpful assistant.")
    response = chat("What's your purpose?")
    assert "helpful assistant" in response.lower()

def test_stream_response():
    chat = Chatette()
    stream = chat("Tell me a story.", stream=True)
    chunks = list(stream)
    assert len(chunks) > 1
    assert isinstance(chunks[0], str)

def test_image_input():
    chat = Chatette()
    image_filename = "test_image.jpg"
    with open(image_filename, "wb") as f:
        f.write(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="))
    
    response = chat("What's in this image?", images=[image_filename])
    assert isinstance(response, str)
    assert len(response) > 0

def test_tool_usage():
    def get_weather(
        location: str,  # The city and state, e.g. San Francisco, CA
        unit: str = "celsius"  # The temperature unit (celsius or fahrenheit)
    ) -> dict:  # Returns a dictionary with weather information
        """Get the current weather in a given location."""
        return {"temperature": 22, "unit": unit, "condition": "Sunny"}

    chat = Chatette()
    chat.add_tool(get_weather)
    response = chat("What's the weather like in New York?")
    assert "22" in response
    assert "celsius" in response.lower()
    assert "Sunny" in response

def test_token_usage():
    chat = Chatette()
    chat("Hello")
    assert chat.total_tokens > 0
    assert chat.prompt_tokens > 0
    assert chat.completion_tokens > 0

def test_custom_headers():
    chat = Chatette(http_referer="https://myapp.com", x_title="My Cool App")
    response = chat("Hello")
    assert isinstance(response, str)

def test_require_json():
    chat = Chatette()
    response = chat("List three colors in JSON format", require_json=True)
    # require_json=True is equivalent to response_format={"type": "json_object"}
    assert isinstance(response, dict)
    assert "colors" in response

def test_error_handling():
    chat = Chatette()
    with pytest.raises(ChatetteError):
        chat("This should fail", model="nonexistent/model")

def test_stream_cancellation():
    chat = Chatette()
    stream = chat("Tell me a very long story.", stream=True)
    chunks = []
    for i, chunk in enumerate(stream):
        chunks.append(chunk)
        if i == 5:
            stream.cancel()
            break
    assert len(chunks) <= 6

@responses.activate
def test_url_context():
    url = "https://example.com/article"
    responses.add(responses.GET, url, 
                  body="# Test Article\n\nThis is a test article content.",
                  status=200,
                  content_type="text/html")

    chat = Chatette()
    response = chat("Summarize the article I provided", urls=[url])
    
    assert "Test Article" in response
    assert "test article content" in response.lower()

def test_temperature():
    chat = Chatette()
    
    prompt = "Generate a random number between 1 and 10"
    response_low = chat(prompt, temperature=0.1)
    response_high = chat(prompt, temperature=0.9)
    
    assert response_low != response_high

def test_max_tokens():
    chat = Chatette()
    short_response = chat("Tell me a story", max_tokens=10)
    long_response = chat("Tell me a story", max_tokens=100)
    
    assert len(short_response.split()) < len(long_response.split())

def test_stop_sequence():
    chat = Chatette()
    response = chat("Count from 1 to 10", stop=["5"])
    numbers = [int(s) for s in response.split() if s.isdigit()]
    assert max(numbers) <= 5

def test_tool_choice():
    def get_weather(location: str) -> dict:
        """Get the current weather in a given location."""
        return {"temperature": 22, "condition": "Sunny"}

    def get_time(location: str) -> str:
        """Get the current time in a given location."""
        return "12:00 PM"

    chat = Chatette()
    chat.add_tool(get_weather)
    chat.add_tool(get_time)

    response = chat("What's the weather and time in New York?", tool_choice="get_weather")
    assert "22" in response
    assert "Sunny" in response
    assert "12:00 PM" not in response

def test_provider_preferences():
    chat = Chatette()
    response = chat("Hello", provider_preferences={"openai": {"weight": 1}, "anthropic": {"weight": 2}})
    assert isinstance(response, str)

def test_add_conversation_history():
    chat = Chatette()
    chat.addUser("What's the capital of France?")
    chat.addAssistant("The capital of France is Paris.")
    chat.addUser("What's its population?")
    response = chat("Summarize our conversation.")
    assert "France" in response
    assert "Paris" in response
    assert "population" in response

if __name__ == "__main__":
    pytest.main()
