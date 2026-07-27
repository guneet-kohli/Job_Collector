# import json
# import requests

# OLLAMA_URL = "http://localhost:11434/api/generate"

# # Change this if you prefer another model
# MODEL = "qwen2.5:14b"


# def generate(prompt: str) -> str:
#     response = requests.post(
#         OLLAMA_URL,
#         json={
#             "model": MODEL,
#             "prompt": prompt,
#             "stream": False,
#             "options": {
#                 "temperature": 0,
#                 "top_p": 1,
#                 "seed": 42,
#             },
#         },
#         timeout=None,
#     )

#     response.raise_for_status()

#     return response.json()["response"]


import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

# MODEL = "llama3.1:8b"
MODEL = "gemma3:4b"


def generate(prompt: str):

    print()
    print("=" * 80)
    print("LLM REQUEST")
    print("=" * 80)
    print(f"Model      : {MODEL}")
    print(f"Characters : {len(prompt):,}")
    print(f"Est Tokens : {len(prompt)//4:,}")
    print()

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0,
                "top_p": 1,
                "top_k": 1,
                "seed": 42,
                "num_ctx": 32768,
                "num_predict": 2048,
            },
        },
        timeout=None,
    )

    response.raise_for_status()

    return response.json()["response"]