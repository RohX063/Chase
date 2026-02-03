from actions.search_google import search_google
from brain.llm_handler import summarize_search, detect_intent
from tts.piper_handler import speak
from actions.system_control import open_website, open_application, shutdown_system

import time
import random
import json


def action_response(action_name):
    variations = [
        f"Initiating {action_name} interface.",
        f"Launching {action_name}, sir.",
        f"{action_name} is on the way.",
        f"Bringing up {action_name}.",
        f"Done. Opening {action_name}, sir."
    ]
    return random.choice(variations)


def handle_search(query):
    start = time.time()

    results = search_google(query)
    print("Search time:", time.time() - start)

    mid = time.time()

    summary = summarize_search(query, results)
    print("LLM time:", time.time() - mid)

    print(f"\nChase: {summary}\n")
    speak(summary)

    print("Total time:", time.time() - start)


def main():
    print("Chase is online.\n")

    while True:
        user_input = input("You: ")

        intent_json = detect_intent(user_input)

        try:
            intent_data = json.loads(intent_json)
            print("INTENT DATA:", intent_data)
        except Exception as e:
            print("Intent parse failed.", e)
            print("RAW:", intent_json)
            continue

        intent = intent_data.get("intent")
        target = intent_data.get("target", "").lower().strip()
        query = intent_data.get("query")

        #  WEBSITE OVERRIDE (Always check first)
        if "youtube" in target:
            speak(action_response("YouTube"))
            open_website("https://youtube.com")

        elif "google" in target:
            speak(action_response("Google"))
            open_website("https://google.com")

        #  APPLICATIONS
        elif intent == "open_application":
            speak(action_response(target.title()))
            open_application(target)

        #  SEARCH
        elif intent == "search":
            handle_search(query)

        #  SHUTDOWN
        elif intent == "shutdown":
            speak("Shutting down the system.")
            shutdown_system()

        else:
            speak("I did not understand that command.")


if __name__ == "__main__":
    main()