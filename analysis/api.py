import os
import json
from openai import OpenAI

def get_creds() -> OpenAI:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY not set")
    return OpenAI(api_key=key)

def analyze_with_llm(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini") -> dict:
    client = get_creds()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    text = resp.choices[0].message.content
    return json.loads(text)
