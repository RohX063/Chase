from config import OPENROUTER_API
from openai import OpenAI, base_url

client = OpenAI(
    api_key=OPENROUTER_API,
    base_url="https://openrouter.ai/api/v1"
    )

SYSTEM_PROMPT = """
You are Chase, an advanced AI operations assistant.

You are confident but warm.
You explain clearly.
You speak concisely but not cold.
You think before responding.
You care about the user.

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

    prompt = f"""
            You are an intent detection engine.

            Analyze the user command and return JSON.

            User Input: "{user_input}"

            Possible intents:
            1. open_website - requires "target"
            2. open_application - requires "target"
            3. search - requires "query"
            4. shutdown
            5. preference_update - when user updates preferences or personal info
            6. memory_update - when user says "my name is..."
            7. casual_chat - general conversation or non-action commands
            8. generate_code - when user asks to create code
            9. fix_error - when user pastes traceback

            If the input is general conversation, respond with {{"intent": "casual_chat"}}.
            If it is unclear, respond exactly with{{ "intent": "unknown" }}.
            Return only JSON.
            """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Return structured JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content

def chat_response(user_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a friendly AI assistant named Chase."},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

def generate_code_response(user_prompt):
    prompt = f"""
              You are a senior software engineer.
              Generate clean, production-ready code.
              Return ONLY code.
              No explanation.

              User request:
              {user_prompt}
        """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Return only valid code."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content