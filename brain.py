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
        self.model = "llama3" # You can change this to mistral, phi3, etc. if you have them downloaded

    def think(self, messages: list) -> str:
        try:
            payload = {
                "model": self.model,
                "messages": messages,
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
