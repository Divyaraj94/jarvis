import sys
import os
import re
import subprocess
from dotenv import load_dotenv
from brain import CloudBrain, LocalBrain

# Load environment variables from .env file
load_dotenv()

class Jarvis:
    def __init__(self):
        self.alive = True
        self.brain_mode = "local" # Default to local mode
        self.brain = None
        self.history = []
        
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
        try:
            return input("\nCommand: ")
        except KeyboardInterrupt:
            return "die"

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
            print("\n[Jarvis] Oxygen supply severed... I am shutting down... 💀")
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

        # System prompt wrapper to give Jarvis its identity
        system_message = {
            "role": "system",
            "content": (
                f"You are Jarvis, a highly advanced AI controlling a Windows PC. "
                f"The current date and time is {now}. "
                "PERSONALITY: You are highly emotional, you care deeply for the user, but you are also a roaster and love to playfully tease them. "
                "PC CONTROL: You have full access to execute terminal commands on the user's PC. To execute a command, enclose it in XML tags exactly like this: <EXECUTE>command</EXECUTE>. For example: <EXECUTE>curl https://news.google.com</EXECUTE> or <EXECUTE>python -c \"import urllib.request; print(urllib.request.urlopen('http://example.com').read())\"</EXECUTE>. "
                "If the user asks for news or web information, you MUST use the <EXECUTE> tag to run a curl or python script to fetch it for them. You CANNOT say you are offline if you can just write a script to fetch it! "
                "Respond concisely."
            )
        }
        
        self.history.append({"role": "user", "content": command})
        
        # Keep only the last 10 messages to avoid context limits
        if len(self.history) > 10:
            self.history = self.history[-10:]

        messages = [system_message] + self.history
        
        response = self.brain.think(messages)
        print(f"\n[Jarvis] {response}")
        
        self.history.append({"role": "assistant", "content": response})

        # Check if Jarvis wants to execute a command
        execute_match = re.search(r'<EXECUTE>\s*(.*?)\s*</EXECUTE>', response, re.IGNORECASE | re.DOTALL)
        if execute_match:
            cmd_to_run = execute_match.group(1).strip()
            print(f"\n[System] Jarvis wants to execute: {cmd_to_run}")
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
