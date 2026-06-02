import os
import requests
from google import genai

class Brain:
    def think(self, messages: list) -> str:
        raise NotImplementedError

class CloudBrain(Brain):
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file. Please add it to use Cloud Mode.")
        
        self.client = genai.Client(api_key=api_key)
        
        available_models = []
        try:
            for m in self.client.models.list():
                if 'generateContent' in m.supported_actions:
                    available_models.append(m.name.replace('models/', ''))
        except Exception as e:
            pass

        self.model_name = 'gemini-2.0-flash' # Default fallback
        for m in available_models:
            # We skip 2.0-flash because it hit a quota limit earlier
            if 'flash' in m and '2.0-flash' not in m:
                self.model_name = m
                break
        
        print(f"[System] Dynamically selected Cloud model: {self.model_name}")

    def think(self, messages: list) -> str:
        # Build a single string prompt for Gemini to handle system/user/assistant context
        prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                prompt += f"[System Context]: {msg['content']}\n\n"
            elif msg["role"] == "user":
                prompt += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant":
                prompt += f"Jarvis: {msg['content']}\n"
        prompt += "Jarvis:"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error communicating with Cloud AI: {str(e)}"

class LocalBrain(Brain):
    def __init__(self):
        # Update to Ollama chat endpoint for conversation history
        self.url = "http://localhost:11434/api/chat"
        self.model = "qwen2:1.5b" # You can change this to llama3, mistral, etc. if your PC has enough memory

    def think(self, messages: list) -> str:
        try:
            # Prepend system context to the first user message so local models follow instructions reliably
            formatted_messages = []
            system_content = ""
            for msg in messages:
                if msg["role"] == "system":
                    system_content += msg["content"] + "\n\n"
                else:
                    formatted_messages.append(msg.copy())

            if system_content and formatted_messages:
                for msg in formatted_messages:
                    if msg["role"] == "user":
                        msg["content"] = f"[SYSTEM CONTEXT & INSTRUCTIONS]\n{system_content.strip()}\n\n[USER REQUEST]\n{msg['content']}"
                        break
            elif system_content:
                formatted_messages = [{"role": "user", "content": system_content.strip()}]

            payload = {
                "model": self.model,
                "messages": formatted_messages,
                "stream": False
            }
            # Increased timeout to 120 seconds for complex generations
            response = requests.post(self.url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except requests.exceptions.ConnectionError:
            return "Error: Local AI (Ollama) is not running or installed on your PC. Please start Ollama."
        except Exception as e:
            return f"Error communicating with Local AI: {str(e)}"
