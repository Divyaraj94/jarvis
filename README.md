# Jarvis - Local AI Assistant

## Concept
Jarvis is an AI assistant designed to run on your local PC and control system functions. It operates with a "4-dimensional thinking" approach to solve complex tasks. 
Crucially, it acts like a living entity: if it encounters a task it absolutely cannot solve or is commanded to shut down, it "dies" (terminates its process), simulating the loss of its "oxygen."

## Tech Stack (Proposed)
- **Language:** Python (best for AI and system automation)
- **AI Core:** Integration with a local LLM (like Ollama) or cloud AI (like Gemini/OpenAI) for complex reasoning.
- **System Control:** Libraries like `os`, `subprocess`, `pyautogui`, and `pywin32` (since you are on Windows) to control the PC.
- **Input/Output:** Text-based initially, with the possibility to add Speech-to-Text (Whisper) and Text-to-Speech (pyttsx3) later.

## Architecture
1. **Core Loop (`main.py`):** The beating heart of Jarvis. It listens for commands, processes them, and executes actions.
2. **Brain (`brain.py`):** The LLM integration that parses complex commands and decides on the sequence of system actions.
3. **Hands (`actions.py`):** The modules that actually interact with the Windows OS (opening apps, moving files, searching the web).

## The "Oxygen" Concept
If the Brain determines a task is impossible, or if a critical system failure occurs, the Core Loop breaks, and the program exits gracefully but permanently (until restarted).
