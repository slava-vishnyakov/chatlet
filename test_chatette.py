import os

import pytest
import requests
import responses
from chatette import Chatette, ChatetteError
import base64
import json
from debug import print_user_message, print_assistant_message, print_system_message, print_token_usage, \
    print_streaming_token, print_new_line


def test_init():
    chat = Chatette()
    assert chat.model == "anthropic/claude-3-opus"
    
    custom_chat = Chatette(model="openai/gpt-3.5-turbo")
    assert custom_chat.model == "openai/gpt-3.5-turbo"

def test_send_message():
    chat = Chatette()
    print_new_line()
    print_user_message("Hello, how are you?")
    response = chat("Hello, how are you?")
    print_assistant_message(response)
    print_token_usage(chat.total_tokens, chat.prompt_tokens, chat.completion_tokens)
    assert isinstance(response, str)
    assert len(response) > 0

def test_system_prompt():
    system_prompt = "You are a helpful assistant named Claude. Your favorite color is blue."
    print("\n", end="")
    print_system_message(system_prompt)
    chat = Chatette(system_prompt=system_prompt)
    print_user_message("What's your name and favorite color?")
    response = chat("What's your name and favorite color?")
    print_assistant_message(response)
    print_token_usage(chat.total_tokens, chat.prompt_tokens, chat.completion_tokens)
    assert "Claude" in response
    assert "blue" in response.lower()

def test_stream_response():
    chat = Chatette()
    print("\n", end="")
    print_user_message("Tell me a story in 10 words.")
    stream = chat("Tell me a story in 10 words.", stream=True)
    chunks = []
    for chunk in stream:
        print_streaming_token(chunk)
        chunks.append(chunk)
    print()  # New line after streaming
    print("\n", end="")
    print_token_usage(chat.total_tokens, chat.prompt_tokens, chat.completion_tokens)
    assert len(chunks) > 1
    assert isinstance(chunks[0], str)

def test_image_input():
    chat = Chatette()
    image_filename = "test_image.jpg"
    if not os.path.exists(image_filename):
        data = requests.get("https://api-ninjas.com/images/cats/abyssinian.jpg").content
        with open(image_filename, "wb") as f:
            f.write(data)

    response = chat("What's in this image? (in 10 words or less)", images=[image_filename])
    assert isinstance(response, str)
    assert len(response) > 0
    assert "cat" in response.lower()
    print_token_usage(chat.total_tokens, chat.prompt_tokens, chat.completion_tokens)

def test_estimate_pricing():
    chat = Chatette()
    response = chat("Hello, how are you?")
    assert isinstance(response, str)
    print(f'\nEstimated cost: ${chat.total_usd:.6f}, last request: ${chat.last_request_usd:.6f}')
    assert chat.total_usd > 0
    assert chat.last_request_usd > 0

def test_tool_usage():
    def get_weather(
        location: str,  # The city and state, e.g. San Francisco, CA
        unit: str = "celsius"  # The temperature unit (celsius or fahrenheit)
    ) -> dict:  # Returns a dictionary with weather information
        """Get the current weather in a given location."""
        return {"temperature": 22, "unit": unit, "condition": "Sunny"}

    chat = Chatette()
    response = chat("What's the weather like in location='New York City, NY'? Don't ask follow-up questions.", tools=[get_weather])
    assert chat.tool_called == "get_weather"
    assert chat.tool_args == {"location": "New York City, NY"}
    assert chat.tool_result == {"temperature": 22, "unit": "celsius", "condition": "Sunny"}

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
