import atexit
import os
import re

import pytest
import requests
import responses

from chatlet import Chatlet, ChatletError
from chatlet.debug import print_user_message, print_assistant_message, print_system_message, print_token_usage, \
    print_streaming_token

Chatlet.DEFAULT_MODEL = "openai/gpt-4o-mini"

def test_init():
    chat = Chatlet()
    assert chat.model == Chatlet.DEFAULT_MODEL
    
    custom_chat = Chatlet(model="openai/gpt-3.5-turbo")
    assert custom_chat.model == "openai/gpt-3.5-turbo"

def test_get_rate_limits_and_credits():
    chat = Chatlet()
    response = chat.get_rate_limits_and_credits()
    #print(response)
    assert 'data' in response
    assert 'usage' in response['data']
    assert 'limit' in response['data']
    assert 'rate_limit' in response['data']

def test_get_token_limits():
    chat = Chatlet()
    response = chat.get_token_limits()
    assert 'data' in response
    assert isinstance(response['data'], list)
    assert 'id' in response['data'][0]
    assert 'per_request_limits' in response['data'][0]
    assert 'prompt_tokens' in response['data'][0]['per_request_limits']
    assert 'completion_tokens' in response['data'][0]['per_request_limits']

def test_system_prompt():
    system_prompt = "You are a helpful assistant named Claude. Your favorite color is blue."
    # print("\n", end="")
    # print_system_message(system_prompt)
    chat = Chatlet(system_prompt=system_prompt)
    # print_user_message("What's your name and favorite color?")
    response = chat("What's your name and favorite color?")
    # print_assistant_message(response)
    # print_token_usage(chat.total_tokens, chat.prompt_tokens, chat.completion_tokens)
    assert "Claude" in response
    assert "blue" in response.lower()

def test_stream_response():
    chat = Chatlet()
    #print("\n", end="")
    #print_user_message("Tell me a story in 10 words.")
    stream = chat("Tell me a story in 10 words.", stream=True)
    chunks = []
    for chunk in stream:
        #print_streaming_token(chunk)
        chunks.append(chunk)
    #print()  # New line after streaming
    #print("\n", end="")
    #print_token_usage(chat.total_tokens, chat.prompt_tokens, chat.completion_tokens)
    assert len(chunks) > 1
    assert isinstance(chunks[0], str)

def test_image_input():
    chat = Chatlet(model="anthropic/claude-3.5-sonnet")
    image_filename = "test_image.jpg"
    if not os.path.exists(image_filename):
        data = requests.get("https://api-ninjas.com/images/cats/abyssinian.jpg").content
        with open(image_filename, "wb") as f:
            f.write(data)

    response = chat("What's in this image? (in 10 words or less)", images=[image_filename])
    assert isinstance(response, str)
    assert len(response) > 0
    assert "cat" in response.lower()
    # print_token_usage(chat.total_tokens, chat.prompt_tokens, chat.completion_tokens)

def test_estimate_pricing():
    chat = Chatlet()
    response = chat("Hello, how are you?")
    assert isinstance(response, str)
    #print(f'\nEstimated cost: ${chat.total_usd:.6f}, last request: ${chat.last_request_usd:.6f}')
    assert chat.total_usd > 0
    assert chat.last_request_usd > 0

def test_tool_usage():
    def get_weather(
        location: str,  # The city and state, e.g. San Francisco, CA
        unit: str = "celsius"  # The temperature unit (celsius or fahrenheit)
    ) -> dict:  # Returns a dictionary with weather information
        """Get the current weather in a given location."""
        return {"temperature": 22, "unit": unit, "condition": "Sunny"}

    chat = Chatlet()
    response = chat("What's the weather like in location='New York City, NY'? Don't think, don't ask follow-up questions.", tools=[get_weather])
    assert (response is None) or ('New York' in response)
    assert chat.tool_called == "get_weather"
    assert chat.tool_args == {"location": "New York City, NY"}
    assert chat.tool_result == {"temperature": 22, "unit": "celsius", "condition": "Sunny"}

    response2 = chat('Thank you!')
    assert 'welcome' in response2.lower()
    assert chat.tool_called is None
    assert chat.tool_args is None
    assert chat.tool_result is None

def test_token_usage():
    chat = Chatlet()
    chat("Hello")
    assert chat.total_tokens > 0
    assert chat.prompt_tokens > 0
    assert chat.completion_tokens > 0

def test_custom_headers():
    chat = Chatlet(http_referer="https://myapp.com", x_title="My Cool App")
    response = chat("Hello")
    assert isinstance(response, str)

def test_require_json():
    chat = Chatlet()
    response = chat("List three colors in JSON format", require_json=True)
    assert isinstance(response, dict)
    assert "colors" in response

def test_error_handling():
    chat = Chatlet(model="nonexistent/model")
    with pytest.raises(ChatletError):
        chat("This should fail")

def test_stream_cancellation():
    chat = Chatlet()
    stream = chat("Tell me a story in 50 words.", stream=True)
    chunks = []
    for i, chunk in enumerate(stream):
        chunks.append(chunk)
        if i == 5:
            chat.cancel()
        if i > 7:
            assert False
    assert len(chunks) <= 6

@pytest.mark.flaky(reruns=3, reruns_delay=0)
def test_url_context():
    url = "https://example.com/article"
    chat = Chatlet()
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps.add(responses.GET, url, 
                 body="# title: Test Article\n\ncontent: This is a test article content.",
                 status=200,
                 content_type="text/html")
        
        rsps.add_passthru('https://')
        
        response = chat("Write the title and exact content I provided above", urls=[url], temperature=0.0)
    
        assert "Test Article" in response.lower() or "test article" in response.lower()
        assert "content" in response.lower()

        # Verify that only the URL request was mocked
        assert len(rsps.calls) == 1
        assert rsps.calls[0].request.url == url

@pytest.mark.flaky(reruns=3, reruns_delay=0)
def test_temperature():
    prompt = "Write a story in 5 words"

    model = "openai/gpt-3.5-turbo"
    chat = Chatlet(model=model)
    response_low = chat(prompt, temperature=0.0)

    chat = Chatlet(model=model)
    response_low2 = chat(prompt, temperature=0.0)

    chat = Chatlet(model=model)
    response_high = chat(prompt, temperature=1.0)
    
    assert response_low == response_low2
    assert response_low != response_high

def test_max_tokens():
    chat = Chatlet()
    short_response = chat("Tell me a story", max_tokens=10)
    long_response = chat("Tell me a story", max_tokens=100)
    
    assert len(short_response.split()) < len(long_response.split())

def test_stop_sequence():
    chat = Chatlet()
    response = chat("Count from 1 to 10 (in numbers), like this: 1, 2, 3...", stop=["5"])
    numbers = map(int, re.findall(r'\d+', response))
    assert max(numbers) <= 5

def test_tool_choice():
    def get_weather(location: str) -> dict:
        """Get the current weather in a given location."""
        return {"temperature": 22, "condition": "Sunny"}

    def get_weather_and_time(location: str) -> str:
        """Get the current time in a given location."""
        return "Temperature is 22 degrees and the time is 12:00 PM"

    chat = Chatlet()
    #chat.debug = True

    chat("What's the weather in New York?", tool_choice="get_weather", tools=[get_weather, get_weather_and_time])
    assert chat.tool_called == "get_weather"
    assert chat.tool_args == {"location": "New York"}
    assert chat.tool_result == {"temperature": 22, "condition": "Sunny"}

def test_provider_order_and_fallbacks():
    chat = Chatlet()
    # expect this to fail because OpenAI is not in the provider_order
    with pytest.raises(ChatletError):
        response = chat("Hello", provider_order=["Anthropic", "Together"], provider_allow_fallbacks=False)

    response = chat("Hello", provider_order=["OpenAI", "Anthropic"], provider_allow_fallbacks=False)

    assert isinstance(response, str)

def test_add_conversation_history():
    chat = Chatlet()
    chat.add_user("What's the capital of France?")
    chat.add_assistant("The capital of France is Paris.")
    chat.add_user("What's its population?")
    response = chat("Summarize our conversation.")
    assert "France" in response
    assert "Paris" in response
    assert "population" in response

# at exit, print total cost
def print_total_cost():
    print(f"Total cost: ${Chatlet.total_usd_sum:.4f}")

atexit.register(print_total_cost)

if __name__ == "__main__":
    pytest.main()
