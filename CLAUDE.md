# JARVIS Project Guide

## Project Vision
A personal autonomous AI assistant that lives on the desktop, acting as an intelligent companion and computer operator. It features a hybrid AI brain (local/cloud), long-term memory, computer control capabilities, and a futuristic UI.

## Core Principles
- **Entity-First:** JARVIS is an entity, not a chatbot. It should have a consistent personality (witty, caring, professional) and a sense of "existence" (the oxygen metaphor).
- **Privacy & Safety:** High-risk actions (file deletion, system changes) always require explicit user confirmation.
- **Modularity:** Use a multi-agent architecture to separate concerns (Planning, Research, Coding, Automation, Memory, Health).
- **Hybrid AI:** Support seamless transition between offline (Ollama/Local) and online (Gemini/Cloud) modes.

## Tech Stack
- **Backend:** Python 3.x
- **AI Brain:** Google GenAI (Cloud), Ollama (Local)
- **Memory:** SQLite (Structured), ChromaDB (Semantic/Vector)
- **Automation:** PyAutoGUI, OS APIs, subprocess
- **Voice:** Whisper (STT), Piper/Coqui (TTS), OpenWakeWord/Porcupine (Wake Word)
- **Vision:** Multimodal LLMs, OCR (Tesseract/EasyOCR)
- **Frontend:** Electron, React, Three.js, WebGL

## Development Workflow
- **Coding Style:** Pythonic, well-documented, modular.
- **Naming:** Clear, descriptive names for agents and actions.
- **Verification:** All new "hands" (actions) must be tested via `test_*.txt` files or a dedicated test suite.
- **Memory Management:** Ensure long-term memory is persisted and retrievable via semantic search.

## Architecture Map
- `main.py`: Entry point, core loop, system command handler.
- `brain.py`: AI model integration and prompt management.
- `memory/`: Long-term storage (SQLite/ChromaDB).
- `actions/`: Modules for computer control (File system, App management, UI automation).
- `voice/`: Speech-to-text and Text-to-speech logic.
- `vision/`: Screen analysis and OCR.
- `agents/`: Specialized agent definitions.
