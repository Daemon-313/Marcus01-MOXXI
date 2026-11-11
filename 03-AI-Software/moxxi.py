from voice_settings import voice_enabled, set_voice_enabled
from voice_router import speak
from conversation import recall_conversation
from conversation import respond
from history import record_exchange

from datetime import datetime
from personality import get_personality
from memory import load_memory, save_memory

MOXXI_PERSONALITY = get_personality()


NAME = "MOXXI"




def main():
    memory = load_memory()
    memory["conversations"] = memory.get("conversations", 0) + 1
    save_memory(memory)

    print("=" * 45)
    print("        MARCUS-01 | MOXXI AI SYSTEM")
    print("=" * 45)
    
    print(f"{MOXXI_PERSONALITY['name']}: Well, hello there, sugar!")

    print("MOXXI: Type 'help' for commands or 'exit' to quit.")

    while True:
        try:
            message = input("\nYOU: ").strip()
            voice_command = message.strip().lower()
            if voice_command in ("voice on", "voice off", "voice status"):
                if voice_command == "voice on":
                    set_voice_enabled(True)
                    print("MOXXI: Voice enabled, sugar!")
                elif voice_command == "voice off":
                    set_voice_enabled(False)
                    print("MOXXI: Voice disabled. I will stay quiet, darling.")
                else:
                    state = "enabled" if voice_enabled() else "disabled"
                    print(f"MOXXI: My voice is {state}, sugar.")
                continue
        except (KeyboardInterrupt, EOFError):
            print("\nMOXXI: Catch you later, darling!")
            break

        if message.lower() in ("exit", "quit", "goodbye"):
            print("MOXXI: Catch you later, darling!")
            if voice_enabled():
                speak("Catch you later, darling!")
            break

        if not message:
            continue

        recalled = recall_conversation(message)

        if recalled is not None:
            reply = recalled
        else:
            reply = respond(message, memory)
        print(f"MOXXI: {reply}")
        if voice_enabled() and not speak(reply):
            print('MOXXI: Voice output unavailable.')
        record_exchange(message, reply)


if __name__ == "__main__":
    main()
