#!/usr/bin/env python3

"""
Example script showing two scenarios:
  1) Starting a new chat conversation
  2) Continuing an existing chat conversation

Make sure your macOS Safari (or Chrome) is open and set up for ChatGPT automation.
"""

from gpt.init import ChatGPT

def start_new_chat_example():
    """
    Demonstrates starting a brand new ChatGPT conversation
    by specifying chat_id='new'.
    """
    # Create a ChatGPT instance with desired window size
    chat = ChatGPT(window_geometry=(0, 0, 700, 900))

    prompt_text = "Hello GPT, let's start fresh. How are you?"
    
    # chat_id='new' forces a brand new conversation
    response = chat.chat(
        prompt=prompt_text,
        chat_id='new',          # <--- new conversation
        model_name='o4-mini-high',
        search=True,
        deep_research=False
    )
    print("\n=== New Chat Response ===\n", response)

def old_chat_example():
    """
    Demonstrates sending a prompt to an existing conversation
    by specifying the known chat_id.
    """
    # Same usage, just different chat_id (replace with your real chat ID)
    chat_id_existing = "68077030-8c80-800d-a020-898bb641dff4"
    chat = ChatGPT(window_geometry=(0, 0, 700, 900))

    prompt_text = "We were discussing quantum physics. Can you continue from where we left off?"
    
    # Provide an existing chat_id to resume the conversation
    response = chat.chat(
        prompt=prompt_text,
        chat_id=chat_id_existing,  # <--- existing conversation
        model_name='o4-mini-high',
        search=False,
        deep_research=True
    )
    print("\n=== Existing Chat Response ===\n", response)

def main():
    # Run both examples in sequence, or pick one as needed
    start_new_chat_example()
    old_chat_example()

if __name__ == "__main__":
    main()
