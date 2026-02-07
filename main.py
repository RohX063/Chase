from networkx import volume
from actions.code_writer import fix_error, generate_code, save_file
from actions.search_google import search_google
from brain.llm_handler import summarize_search, detect_intent
from tts.piper_handler import speak
from actions.system_control import open_website, open_application, shutdown_system
from memory.memory_handler import (
    set_memory,
    get_memory,
    update_profile,
    get_profile,
    update_context,
    get_context,
)
from logs.logger import log_intent, log_error, log_command
from stt.voice_input import listen
import sounddevice as sd

import time
import random
import json, re


def action_response(action_name):
    variations = [
        f"Initiating {action_name} interface.",
        f"Launching {action_name}, sir.",
        f"{action_name} is on the way.",
        f"Bringing up {action_name}.",
        f"Done. Opening {action_name}, sir."
        f"Starting {action_name}"
    ]
    return random.choice(variations)


def handle_search(query):

    start = time.time()

    results = search_google(query)
    summary = summarize_search(query, results)

    print(f"\nChase: {summary}\n")
    speak(summary)

    print("Total time:", time.time() - start)


def main():
    print("Chase is online.\n")

    while True:
     
        #=============
        # Voice STT
        #=============

     mode = input("Press Enter for voice or type command: ")

     if mode == "":
        user_input = listen()
     else:
        user_input = mode
        
        if not user_input:
            continue

        user_input = user_input.lower()
        user_input = re.sub(r"[^\w\s]", "", user_input)

        print("USER INPUT:", user_input)
        print("RAW INTENT JSON:", intent_json)
        print("PARSED INTENT:", intent_data)

        intent_json = detect_intent(user_input)
        intent_data = json.loads(intent_json)

        intent = intent_data.get("intent")
        target = intent_data.get("target", "").lower()
        query = intent_data.get("query")

        try:
            intent_json = detect_intent(user_input)
            log_command(user_input)
            intent_data = json.loads(intent_json)
            intent_name = intent_data.get("intent", "unknown")
            
        except Exception as e:
            print("REAL ERROR:", str(e))
            log_error(str(e))
            speak("An error occurred while processing your request.")
            continue

        try:
            intent_data = json.loads(intent_json)
        except:
            response = summarize_search(user_input, "")
            speak(response)
            continue

        intent = intent_data.get("intent")
        target = intent_data.get("target", "").lower().strip()
        query = intent_data.get("query")

        name = get_memory("name")
        context = get_context()
        profile = get_profile()

        # ======================
        # MEMORY UPDATE (NAME)
        # ======================
        if "my name is" in user_input.lower():
            extracted = user_input.lower().replace("my name is", "").strip().title()
            set_memory("name", extracted)
            speak(f"Understood. I will remember that, {extracted}.")
            continue

        # ======================
        # PREFERENCE 
        # ======================
        if intent == "preference_update":
            if "brave" in user_input.lower():
                update_profile("preferred_browser", "brave")
                speak("Got it. I've set your preferred browser to Brave.")
            else:
                speak("Preference saved.")
            continue

        # ======================
        # WEBSITE 
        # ======================
        if intent == "open_website":

            if "youtube" in target:
                response = action_response("YouTube")
                if name:
                    response = f"{response}, {name}."
                speak(response)

                open_website("https://youtube.com")
                update_context("last_app", "youtube")
                update_context("last_action", "open")
                continue

            if "google" in target:
                speak(action_response("Google"))
                open_website("https://google.com")
                continue

        # ======================
        # APPLICATIONS
        # ======================
        if intent == "open_application":
            speak(action_response(target.title()))
            open_application(target)
            continue

        # ======================
        # SMART SEARCH 
        # ======================
        if intent == "search":
            if context.get("last_app") == "youtube":
                open_website(
                    f"https://youtube.com/results?search_query={query}"
                )
            else:
                handle_search(query)
            continue

        elif intent == "casual_chat":
            response = summarize_search(user_input, "")
            speak(response)
            continue

        elif intent == "generate_code":
             code = generate_code(query)
             filename = "generated_code.py"
             save_file(filename, code)
             speak("Code generated successfully.")

        elif intent == "fix_error":
             with open("generated_code.py", "r") as f:
               old_code = f.read()

             fixed = fix_error(query, old_code)
             save_file("generated_code.py", fixed)
             speak("Error fixed successfully.")


        # ======================
        # SHUTDOWN
        # ======================
        if intent == "shutdown":
            speak("Shutting down the system.")
            shutdown_system()
            continue

        speak("I did not understand that command.")




if __name__ == "__main__":
    main()
