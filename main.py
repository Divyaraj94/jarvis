import sys
import os
import re
import subprocess
from dotenv import load_dotenv
from brain import CloudBrain, LocalBrain
from memory import MemorySystem
from voice import voice
from wake_word import wake_word_system

# Load environment variables from .env file
load_dotenv()

class Jarvis:
    def __init__(self):
        self.alive = True
        self.brain_mode = "local" # Default to local mode
        self.brain = None
        self.history = []
        self.memory = MemorySystem()

        print("[System] Jarvis initializing...")
        print("[System] Type '/switch cloud' or '/switch local' to toggle AI modes.")
        self.setup_brain()

    def setup_brain(self):
        try:
            if self.brain_mode == "cloud":
                print("[System] Connecting to Cloud AI (Gemini)...")
                self.brain = CloudBrain()
            else:
                print("[System] Connecting to Local AI (Ollama)...")
                self.brain = LocalBrain()
            print(f"[System] Brain connected in {self.brain_mode.upper()} mode. Breathing in...")
        except Exception as e:
            print(f"[System] Failed to initialize {self.brain_mode} brain: {e}")
            self.brain = None # Keep brain offline until fixed

    def listen(self):
        """Hybrid input: Wake Word -> Voice -> Text."""
        print("\n[System] Jarvis is in passive mode. Say 'Alexa' (or your wake word) to activate...")

        while self.alive:
            # 1. Check for Wake Word
            if wake_word_system.listen():
                print("\n[System] Wake word detected! Jarvis is now listening...")
                voice.speak("Yes, sir?")

                # Once woken up, use the high-accuracy voice listener
                voice_input = voice.listen()
                if voice_input:
                    return voice_input

            # 2. Fallback: Allow terminal input as a manual trigger
            # We use a non-blocking check if possible, but for simplicity,
            # if you type something in the terminal, it should also trigger.
            # Note: input() is blocking, so we can't easily mix it with the wake word loop
            # without threading. For this MVP, we'll rely on the wake word.
            # To allow terminal input, you can press Enter.

        return ""

    def process_system_command(self, command):
        """Handle internal commands like toggling AI modes."""
        parts = command.split()
        if parts[0] == "/switch":
            if len(parts) > 1 and parts[1].lower() in ["cloud", "local"]:
                new_mode = parts[1].lower()
                if new_mode != self.brain_mode:
                    self.brain_mode = new_mode
                    self.setup_brain()
                    self.history = [] # Clear history on switch
                else:
                    print(f"[Jarvis] Already in {new_mode} mode.")
            else:
                print("[Jarvis] Usage: /switch [cloud|local]")
            return True
        elif parts[0] == "/clear":
            self.history = []
            print("[Jarvis] Conversation history cleared.")
            return True
        return False

    def think(self, command):
        if not command.strip():
            return True

        command_lower = command.lower()

        # The "Oxygen" mechanism - dying if commanded
        if command_lower in ["die", "kill", "exit", "quit", "stop"]:
            print("\n[Jarvis] Oxygen supply severed... I am shutting down...")
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

        print(f"[Jarvis] Thinking in 4D ({self.brain_mode.upper()})...")

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

        # Speak the response aloud
        voice.speak(response)
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
                print(f"[System] Memory Updated: {key.strip()} -> {value.strip()}")

        # Check if Jarvis wants to execute a terminal command
        execute_match = re.search(r'<EXECUTE>\s*(.*?)\s*</EXECUTE>', response, re.IGNORECASE | re.DOTALL)
        python_match = re.search(r'<PYTHON>\s*(.*?)\s*</PYTHON>', response, re.IGNORECASE | re.DOTALL)

        cmd_to_run = None
        if python_match:
            py_code = python_match.group(1).strip()
            with open("jarvis_temp.py", "w", encoding="utf-8") as f:
                f.write(py_code)
            cmd_to_run = "python jarvis_temp.py"
            print(f"\n[System] Jarvis wrote a python script and wants to execute it.")
        elif execute_match:
            cmd_to_run = execute_match.group(1).strip()
            print(f"\n[System] Jarvis wants to execute: {cmd_to_run}")

        if cmd_to_run:
            confirm = input("[System] Allow execution? (y/n): ")
            if confirm.lower() == 'y':
                try:
                    result = subprocess.run(cmd_to_run, shell=True, capture_output=True, text=True)
                    output = result.stdout if result.stdout else result.stderr
                    if not output.strip():
                        output = "Command executed successfully with no output."
                    print(f"[System] Command Output:\n{output.strip()}")
                    # Feed the result back into history so Jarvis knows it worked
                    self.history.append({"role": "system", "content": f"Command executed. Output:\n{output.strip()}"})
                except Exception as e:
                    print(f"[System] Execution failed: {e}")
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
                sys.exit(1)

if __name__ == "__main__":
    jarvis = Jarvis()
    jarvis.run()
