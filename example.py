#!/usr/bin/env python3

"""
Example script showing two scenarios:
  1) Starting a new chat conversation
  2) Continuing an existing chat conversation

After sending a prompt, we also print the chat ID and the response.
"""

from gpt.init import ChatGPT

def start_new_chat_example():
    """
    Demonstrates starting a brand new ChatGPT conversation
    by specifying chat_id='new', then prints the chat ID and the response.
    """
    chat = ChatGPT(window_geometry=(0, 0, 700, 900))

    prompt_text = "Hello GPT, let's start fresh. How are you?"
    
    # chat_id='new' forces a brand new conversation
    response = chat.chat(
        prompt=prompt_text,
        chat_id='new',
        model_name='o4-mini-high',
        search=True,
        deep_research=False
    )
    
    # Retrieve and print the new chat ID, plus the response
    new_chat_id = chat.get_chat_id()
    print("\n=== New Chat ===")
    print("Chat ID:", new_chat_id)
    print("Response:", response)

def old_chat_example():
    """
    Demonstrates sending a prompt to an existing conversation
    by specifying the known chat_id, then prints the chat ID and the response.
    """
    # Replace with your actual existing chat ID
    existing_chat_id = "680e430b-d554-8003-92ad-362c567e1975"
    chat = ChatGPT(window_geometry=(0, 0, 700, 900))

    prompt_text = "We were discussing quantum physics. Can you continue from where we left off?"
    
    response = chat.chat(
        prompt=prompt_text,
        chat_id=existing_chat_id,
        model_name='o4-mini-high',
        search=False,
        deep_research=True
    )

    # Retrieve and print the continuing chat ID, plus the response
    resumed_chat_id = chat.get_chat_id()
    print("\n=== Existing Chat ===")
    print("Chat ID:", resumed_chat_id)
    print("Response:", response)

def main():
    # Run both examples in sequence
    #start_new_chat_example()
    old_chat_example()

if __name__ == "__main__":
    main()
