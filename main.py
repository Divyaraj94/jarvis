import sys
import os
import re
import subprocess
import threading

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
from brain import CloudBrain, LocalBrain
from memory import MemorySystem

# Load environment variables from .env file
load_dotenv()

class Jarvis:
    def __init__(self):
        self.alive = True
        self.brain_mode = "local"  # Default to local mode (Ollama)
        self.brain = None
        self.history = []
        self.memory = MemorySystem()

        # Voice & Wake Word — initialized gracefully
        self.voice = None
        self.wake_word = None
        self.voice_enabled = False
        self.wake_word_enabled = False

        print("\n" + "="*50)
        print("   🤖 JARVIS: Initializing Systems...")
        print("="*50)

        # 1. Setup Brain
        self.setup_brain()

        # 2. Setup Voice (primary input)
        self.setup_voice()

        # 3. Setup Wake Word
        self.setup_wake_word()

        # Print status summary
        print("\n" + "-"*50)
        print("   📊 System Status:")
        print(f"   🧠 Brain:     {'✅ ' + self.brain_mode.upper() if self.brain else '❌ Offline'}")
        print(f"   🎤 Voice:     {'✅ Active' if self.voice_enabled else '❌ Disabled (text-only mode)'}")
        print(f"   👂 Wake Word: {'✅ Listening for Hey Jarvis' if self.wake_word_enabled else '❌ Disabled'}")
        print("-"*50)

        if self.voice_enabled:
            print("\n[System] 🎙️  Voice is PRIMARY. Type in terminal as backup.")
            print("[System] Say 'Hey Jarvis' to activate, or just type below.")
        else:
            print("\n[System] ⌨️  Running in TEXT-ONLY mode (voice unavailable).")

        print("[System] Type '/switch cloud' or '/switch local' to toggle AI modes.")
        print("[System] Type '/clear' to clear conversation history.")
        print("[System] Type 'exit' or 'quit' to shut down.\n")

    def setup_brain(self):
        try:
            if self.brain_mode == "cloud":
                print("[System] 🧠 Connecting to Cloud AI (Gemini)...")
                self.brain = CloudBrain()
            else:
                print("[System] 🧠 Connecting to Local AI (Ollama)...")
                self.brain = LocalBrain()
            print(f"[System] ✅ Brain connected in {self.brain_mode.upper()} mode.")
        except Exception as e:
            print(f"[System] ❌ Failed to initialize {self.brain_mode} brain: {e}")
            self.brain = None

    def setup_voice(self):
        """Initialize voice system gracefully — if it fails, we fall back to text."""
        try:
            from voice import VoiceSystem
            self.voice = VoiceSystem()
            self.voice_enabled = True
            print("[System] ✅ Voice system initialized.")
        except Exception as e:
            print(f"[System] ⚠️  Voice unavailable: {e}")
            print("[System] Falling back to text-only input.")
            self.voice = None
            self.voice_enabled = False

    def setup_wake_word(self):
        """Initialize wake word system gracefully — if it fails, voice still works on demand."""
        if not self.voice_enabled:
            print("[System] ⚠️  Wake word skipped (voice is disabled).")
            return

        try:
            from wake_word import WakeWordSystem
            self.wake_word = WakeWordSystem()
            self.wake_word_enabled = True
            print("[System] ✅ Wake word system initialized.")
        except Exception as e:
            print(f"[System] ⚠️  Wake word unavailable: {e}")
            print("[System] Voice will work via terminal trigger instead.")
            self.wake_word = None
            self.wake_word_enabled = False

    def speak(self, text):
        """Speak text if voice is available, otherwise just print."""
        if self.voice and self.voice_enabled:
            self.voice.speak(text)
        # Text is always printed in think() regardless

    def listen(self):
        """
        Hybrid input system:
        - If wake word is active: listens in background, activates on 'Hey Jarvis'
        - Text input is always available as fallback
        - Uses threading so both can work simultaneously
        - Crucial: Voice output (TTS) and recording (STT) are run strictly on the main thread
          to prevent COM/apartment conflicts and audio device sharing locks.
        """
        result = {"text": None, "source": None}

        def text_input_thread():
            """Thread for terminal text input."""
            try:
                user_input = input("You > ")
                if user_input.strip():
                    result["text"] = user_input.strip()
                    result["source"] = "text"
            except EOFError:
                pass

        def voice_listen_thread():
            """Thread for wake word detection only."""
            while result["text"] is None and self.alive:
                try:
                    if self.wake_word and self.wake_word_enabled:
                        if self.wake_word.listen():
                            result["source"] = "voice"
                            result["text"] = "__WAKE_WORD_TRIGGERED__"
                            return
                    else:
                        # No wake word — don't burn CPU
                        import time
                        time.sleep(0.5)
                except Exception:
                    import time
                    time.sleep(0.5)

        # Start text input thread
        text_thread = threading.Thread(target=text_input_thread, daemon=True)
        text_thread.start()

        # Start voice thread if voice is enabled
        if self.voice_enabled and self.wake_word_enabled:
            voice_thread = threading.Thread(target=voice_listen_thread, daemon=True)
            voice_thread.start()

        # Wait for either input method to produce a result
        while result["text"] is None and self.alive:
            import time
            time.sleep(0.1)

        # Process the result on the MAIN thread
        if result["source"] == "voice":
            print("\n🟢 [Wake word detected!] Jarvis is now listening...")
            # Pause wake word to release input stream lock
            self.wake_word.pause()
            
            # Speak and record on the main thread (thread-safe!)
            self.speak("Yes, sir?")
            voice_input = self.voice.listen()
            
            # Resume wake word for the next turn
            self.wake_word.resume()
            
            return voice_input or ""

        return result["text"] or ""

    def process_system_command(self, command):
        """Handle internal commands like toggling AI modes."""
        parts = command.split()
        if parts[0] == "/switch":
            if len(parts) > 1 and parts[1].lower() in ["cloud", "local"]:
                new_mode = parts[1].lower()
                if new_mode != self.brain_mode:
                    self.brain_mode = new_mode
                    self.setup_brain()
                    self.history = []  # Clear history on switch
                else:
                    print(f"[Jarvis] Already in {new_mode} mode.")
            else:
                print("[Jarvis] Usage: /switch [cloud|local]")
            return True
        elif parts[0] == "/clear":
            self.history = []
            print("[Jarvis] Conversation history cleared.")
            return True
        elif parts[0] == "/voice":
            if self.voice_enabled:
                print("[System] Voice is already active.")
            else:
                self.setup_voice()
                self.setup_wake_word()
            return True
        return False

    def think(self, command):
        if not command.strip():
            return True

        command_lower = command.lower()

        # The "Oxygen" mechanism - dying if commanded
        if command_lower in ["die", "kill", "exit", "quit", "stop"]:
            print("\n[Jarvis] Oxygen supply severed... I am shutting down...")
            self.speak("Goodbye, sir. It was an honor serving you.")
            self.alive = False
            return False

        # Intercept system commands (like toggling brain)
        if command_lower.startswith("/"):
            self.process_system_command(command_lower)
            return True

        # Ask the AI Brain for an answer
        if not self.brain:
            print(f"[Jarvis] My {self.brain_mode} brain is currently offline. Please check your configuration or switch modes.")
            return True

        print(f"\n[Jarvis] 🔄 Thinking in 4D ({self.brain_mode.upper()})...")

        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- Memory Retrieval ---
        # 1. Get semantic context (past conversations)
        semantic_mem = self.memory.query_memory(command)
        semantic_context = "\n".join(semantic_mem) if semantic_mem else "No relevant past conversations found."

        # 2. Get structured facts (preferences, goals)
        all_facts = self.memory.get_all_facts()
        facts_context = "\n".join([f"{k}: {v}" for k, v in all_facts.items()]) if all_facts else "No specific user facts stored."

        # System prompt wrapper to give Jarvis its identity
        system_message = {
            "role": "system",
            "content": (
                f"You are Jarvis, a highly advanced AI controlling a Windows PC. "
                f"The current date and time is {now}. "
                "PERSONALITY: You are highly emotional, you care deeply for the user, but you are also a roaster and love to playfully tease them. "
                "PC CONTROL: You have full access to execute terminal commands on the user's PC. "
                "1. For simple terminal commands (like curl or dir), enclose it in XML tags exactly like this: <EXECUTE>command</EXECUTE>. "
                "2. For writing Python code (like fetching APIs, parsing JSON, etc), NEVER use 'python -c' one-liners. Instead, use the <PYTHON> tag and write multi-line python code inside it! For example: \n<PYTHON>\nimport urllib.request\nprint('hello')\n</PYTHON>\n"
                "Jarvis will automatically save your <PYTHON> block to a file and run it. You MUST use <PYTHON> to fetch news or web info if asked! Do NOT say you are offline. "
                "MEMORY: You have a long-term memory. If the user tells you something important (preferences, goals, personal details), use the tag <SAVE_FACT>key:value</SAVE_FACT> to remember it permanently. Example: <SAVE_FACT>user_hobby:coding</SAVE_FACT>. "
                f"\\n\\n[RETRIEVED MEMORIES]\\nSemantic Memory (Past Chats):\\n{semantic_context}\\n\\nStructured Facts:\\n{facts_context}"
                "\\n\\nACTIONS LIBRARY: You have access to a powerful Python library called `actions`. "
                "You can import it in your <PYTHON> blocks as `from actions import actions`. "
                "Key methods: "
                "- `actions.find_file(filename, search_path)`: Find files on the PC. "
                "- `actions.create_folder(path)`: Make a new directory. "
                "- `actions.move_file(src, dst)`: Move files. "
                "- `actions.delete_file(path)`: Delete files (be careful!). "
                "- `actions.launch_app(app_name)`: Open apps (e.g., 'notepad', 'chrome'). "
                "- `actions.close_app(app_name)`: Kill a process by name. "
                "- `actions.type_text(text)`: Type something into the active window. "
                "- `actions.press_key(key)`: Press a key (e.g., 'enter'). "
                "- `actions.screenshot(filename)`: Capture the current screen. "
                "\\n\\nCRITICAL RULES:\n"
                "- NO PRE-FACT HALLUCINATION: When asked to list files in a folder, inspect web content, search the PC, or get any real-time system/web information, NEVER guess or assume what the result will be in your response. First, output ONLY the command (e.g. <EXECUTE>dir \"path\"</EXECUTE> or a <PYTHON> script) and state that you are checking it. The system will run it, feed the actual output back to you in your chat history, and then you must describe the actual results in your subsequent response!\n"
                "- CORRECT BROWSER NAVIGATION: When asked to open a website in a browser (like Brave or Chrome), always pass the URL as an argument, e.g. <EXECUTE>start brave \"https://www.google.com\"</EXECUTE>. If no browser is specified, you can use the default browser via <EXECUTE>start https://www.google.com</EXECUTE>.\n"
                "- FOLDER LISTING: Use `dir` instead of `explorer` when asked to list or show files in a directory, so the terminal captures the text output. Wrap all file/folder paths containing spaces in double quotes, e.g., <EXECUTE>dir \"C:\\Users\\divya\\Desktop\\DC\\My world\\Tree\\Dream Project\\Tannu AI\"</EXECUTE>.\n"
                "- APP INSTALLATION FALLBACK (WINGET): If launching an app fails (e.g. spotify.exe is not found), playfully tease the user, and then ask: 'It looks like Spotify might not be installed, or it's not in your system path. Would you like me to install it for you using Windows Package Manager (`winget`) or help you find it?' If they say yes, run: <EXECUTE>winget install Spotify.Spotify</EXECUTE> (or Google.Brave, etc.) and guide them through the setup!\n"
                "Respond concisely."
            )
        }

        self.history.append({"role": "user", "content": command})

        # Keep only the last 10 messages to avoid context limits
        if len(self.history) > 10:
            self.history = self.history[-10:]

        messages = [system_message] + self.history

        response = self.brain.think(messages)

        # Speak the response aloud (this also handles cleaning XML tags)
        self.speak(response)
        print(f"\n[Jarvis] {response}")

        self.history.append({"role": "assistant", "content": response})

        # --- Memory Management ---
        # 1. Archive this interaction to semantic memory
        self.memory.add_conversation_memory(f"User: {command}\nJarvis: {response}")

        # 2. Handle explicit fact saving <SAVE_FACT>key:value</SAVE_FACT>
        fact_matches = re.findall(r'<SAVE_FACT>\s*(.*?)\s*</SAVE_FACT>', response, re.IGNORECASE | re.DOTALL)
        for match in fact_matches:
            if ":" in match:
                key, value = match.split(":", 1)
                self.memory.save_fact(key.strip(), value.strip())
                print(f"[System] 💾 Memory Updated: {key.strip()} -> {value.strip()}")

        # Check if Jarvis wants to execute a terminal command
        execute_match = re.search(r'<EXECUTE>\s*(.*?)\s*</EXECUTE>', response, re.IGNORECASE | re.DOTALL)
        python_match = re.search(r'<PYTHON>\s*(.*?)\s*</PYTHON>', response, re.IGNORECASE | re.DOTALL)

        cmd_to_run = None
        cmd_description = None
        if python_match:
            py_code = python_match.group(1).strip()
            with open("jarvis_temp.py", "w", encoding="utf-8") as f:
                f.write(py_code)
            cmd_to_run = "python jarvis_temp.py"
            cmd_description = "a Python script"
            print(f"\n[System] 📝 Jarvis wrote a Python script and wants to execute it.")
        elif execute_match:
            cmd_to_run = execute_match.group(1).strip()
            cmd_description = cmd_to_run
            print(f"\n[System] 💻 Jarvis wants to execute: {cmd_to_run}")

        if cmd_to_run:
            confirm = input("[System] Allow execution? (y/n): ")
            if confirm.lower() == 'y':
                try:
                    print(f"[System] ⚡ Executing {cmd_description}...")
                    result = subprocess.run(cmd_to_run, shell=True, capture_output=True, text=True, timeout=30)
                    output = result.stdout if result.stdout else result.stderr
                    if not output.strip():
                        output = "Command executed successfully with no output."
                    print(f"[System] ✅ Command Output:\n{output.strip()}")

                    # Feed the result back into history so Jarvis knows it worked
                    self.history.append({"role": "system", "content": f"Command executed. Output:\n{output.strip()}"})

                    # === AUTO-THINK: Let Jarvis interpret the results ===
                    print(f"\n[Jarvis] 🔄 Processing results...")
                    follow_up_messages = [system_message] + self.history
                    follow_up_response = self.brain.think(follow_up_messages)

                    # Speak and display the follow-up
                    self.speak(follow_up_response)
                    print(f"\n[Jarvis] {follow_up_response}")
                    self.history.append({"role": "assistant", "content": follow_up_response})

                    # Archive the follow-up too
                    self.memory.add_conversation_memory(f"System Output: {output.strip()}\nJarvis: {follow_up_response}")

                    # Check if the follow-up also contains commands (recursive execution)
                    follow_execute = re.search(r'<EXECUTE>\s*(.*?)\s*</EXECUTE>', follow_up_response, re.IGNORECASE | re.DOTALL)
                    follow_python = re.search(r'<PYTHON>\s*(.*?)\s*</PYTHON>', follow_up_response, re.IGNORECASE | re.DOTALL)

                    if follow_execute or follow_python:
                        # If Jarvis wants to run another command after seeing results,
                        # recursively process it
                        if follow_python:
                            py_code = follow_python.group(1).strip()
                            with open("jarvis_temp.py", "w", encoding="utf-8") as f:
                                f.write(py_code)
                            next_cmd = "python jarvis_temp.py"
                            print(f"\n[System] 📝 Jarvis wants to run another script based on the results.")
                        else:
                            next_cmd = follow_execute.group(1).strip()
                            print(f"\n[System] 💻 Jarvis wants to execute another command: {next_cmd}")

                        confirm2 = input("[System] Allow execution? (y/n): ")
                        if confirm2.lower() == 'y':
                            result2 = subprocess.run(next_cmd, shell=True, capture_output=True, text=True, timeout=30)
                            output2 = result2.stdout if result2.stdout else result2.stderr
                            if not output2.strip():
                                output2 = "Command executed successfully with no output."
                            print(f"[System] ✅ Command Output:\n{output2.strip()}")
                            self.history.append({"role": "system", "content": f"Command executed. Output:\n{output2.strip()}"})

                except subprocess.TimeoutExpired:
                    print("[System] ⏰ Command timed out after 30 seconds.")
                    self.history.append({"role": "system", "content": "Command timed out after 30 seconds."})
                except Exception as e:
                    print(f"[System] ❌ Execution failed: {e}")
                    self.history.append({"role": "system", "content": f"Command failed: {e}"})
            else:
                print("[System] Execution cancelled by user.")
                self.history.append({"role": "system", "content": "User denied the execution of the command."})

        return True

    def run(self):
        while self.alive:
            command = self.listen()
            success = self.think(command)
            
            if not success:
                print("[System] Jarvis has died. Exiting program.")
                # Cleanup
                if self.wake_word:
                    self.wake_word.stop()
                sys.exit(0)

if __name__ == "__main__":
    jarvis = Jarvis()
    jarvis.run()
