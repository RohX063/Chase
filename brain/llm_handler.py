from config import OPENROUTER_API
from openai import OpenAI, base_url

client = OpenAI(
    api_key=OPENROUTER_API,
    base_url="https://openrouter.ai/api/v1"
    )

SYSTEM_PROMPT = """
You are Chase, an advanced AI operations assistant.

give short anwers in only important results the answers must be in 80-90 words maximum.
maintain a professional and concise tone.
"""

def summarize_search(query, search_results):

    content = f"""
User Query: {query}

Search Results:
{search_results}

Provide a concise professional briefing.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content}
        ],
        max_tokens=110,
    )

    return response.choices[0].message.content

def detect_intent(user_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "intent_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string"
                        },
                        "target": {
                            "type": "string"
                        },
                        "query": {
                            "type": "string"
                        }
                    },
                    "required": ["intent"]
                }
            }
        },
        messages=[
            {
                "role": "system",
                "content": "You are an intent detection engine. Return structured JSON."
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        max_tokens=80
    )

    return response.choices[0].message.content