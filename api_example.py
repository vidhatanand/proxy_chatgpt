import openai

openai.api_key = "local-key"         # any string; we don’t check it
openai.base_url = "http://localhost:8000/v1/"

resp = openai.chat.completions.create(
    model="o4-mini-high",
    messages=[{"role": "user", "content": "Hello! How are you?"}],
)
print(resp.choices[0].message.content)