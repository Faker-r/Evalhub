from openai import OpenAI
import os


api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

resp = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="He",
    max_tokens=150,
)

print(resp.choices[0].text)
