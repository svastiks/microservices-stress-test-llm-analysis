import os
import json
from openai import OpenAI


def get_creds() -> OpenAI:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY not set")
    return OpenAI(api_key=key)


def analyze_with_llm(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini") -> dict:
    debug = os.environ.get("LLM_DEBUG", "true").lower() == "true"
    client = get_creds()
    if debug:
        print(
            f"[llm] request_start model={model} "
            f"system_chars={len(system_prompt)} user_chars={len(user_prompt)}"
        )
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    if debug:
        usage = getattr(resp, "usage", None)
        prompt_toks = getattr(usage, "prompt_tokens", None) if usage else None
        completion_toks = getattr(usage, "completion_tokens", None) if usage else None
        total_toks = getattr(usage, "total_tokens", None) if usage else None
        print(
            f"[llm] response_received id={getattr(resp, 'id', 'unknown')} "
            f"prompt_tokens={prompt_toks} completion_tokens={completion_toks} total_tokens={total_toks}"
        )
    text = resp.choices[0].message.content
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        if debug:
            preview = (text or "")[:500].replace("\n", "\\n")
            print(f"[llm] response_parse_failed preview={preview}")
        raise
    if debug:
        print(f"[llm] response_parse_ok keys={sorted(parsed.keys())}")
    return parsed
