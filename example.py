#!/usr/bin/env python3

# Example usage of the ChatGPT class in gpt/init.py
from gpt.init import ChatGPT

def main():
    # Create an instance of the ChatGPT class
    chat = ChatGPT(window_geometry=(0, 0, 700, 900))

    # Example prompt
    prompt_text = "Hello ChatGPT! Can you summarize the importance of sleep?"

    # Send the chat prompt
    try:
        response = chat.chat(
            prompt=prompt_text,
            chat_id="68077030-8c80-800d-a020-898bb641dff4",
            model_name='o4-mini-high',
            search=True,
            deep_research=True
        )
        print("Response from ChatGPT:\n", response)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
