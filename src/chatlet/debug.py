from colorama import Fore, Back, Style, init
import sys

init(autoreset=True)

def print_new_line():
    print("\n", end="")

def print_user_message(message):
    print(f"{Fore.GREEN}User: {message}{Style.RESET_ALL}")

def print_assistant_message(message):
    print(f"{Fore.BLUE}Assistant: {message}{Style.RESET_ALL}")

def print_system_message(message):
    print(f"{Fore.YELLOW}System: {message}{Style.RESET_ALL}")

def print_token_usage(total_tokens, prompt_tokens, completion_tokens):
    print(f"{Fore.MAGENTA}Token Usage: Total: {total_tokens}, Prompt: {prompt_tokens}, Completion: {completion_tokens}{Style.RESET_ALL}")

def print_streaming_token(token):
    if token == '\n':
        sys.stdout.write(f"{Fore.CYAN}{token}{Style.RESET_ALL}")
    else:
        sys.stdout.write(f"{Fore.CYAN}{token}{Style.RESET_ALL}")
    sys.stdout.flush()
