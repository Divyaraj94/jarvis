# 🤖 Jarvis — Local AI Agent for Windows

> A living AI assistant that runs on your PC, thinks with an LLM brain, and controls your system through natural language commands.

---

## 💡 What is Jarvis?

Jarvis is a Python-based AI agent that lives on your local machine. You give it commands in plain English — it thinks, decides what to do, writes and executes code, opens apps, browses the web, and reports back. It supports both **local AI (Ollama/LLaMA)** and **cloud AI (Google Gemini)** as its brain.

Unlike simple chatbots, Jarvis can:
- **Write and run Python scripts** on the fly to fetch data, call APIs, parse JSON
- **Execute terminal commands** directly on your Windows PC
- **Open browsers, apps, and files** via natural language
- **Install missing software** using Windows Package Manager (`winget`)
- **Switch between local and cloud AI** mid-conversation

---

## 🧠 Architecture

```
You (natural language)
        ↓
   main.py (Core Loop)
        ↓
   brain.py (LLM Brain — Local or Cloud)
        ↓
   <EXECUTE> or <PYTHON> tags in response
        ↓
   subprocess runs the command/script
        ↓
   output fed back into conversation history
```

| File | Role |
|------|------|
| `main.py` | Core loop — listens, thinks, executes, loops |
| `brain.py` | LLM integration — Gemini (cloud) or Ollama (local) |
| `jarvis_temp.py` | Auto-generated temp script for Python execution |
| `.env` | API keys (not committed) |

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.10+ |
| Cloud AI | Google Gemini (`gemini-2.0-flash`) via `google-genai` |
| Local AI | Ollama (`llama3`, `mistral`, etc.) |
| System Control | `subprocess`, `os`, `re` |
| Config | `python-dotenv` |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/Divyaraj94/jarvis.git
cd jarvis
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your `.env` file
Create a `.env` file in the root directory:
```
GEMINI_API_KEY=your_gemini_api_key_here
```
Get your free API key at [Google AI Studio](https://aistudio.google.com/)

### 4. Run Jarvis
```bash
python main.py
```

---

## 🗣️ Example Commands

```
Command: Hey Jarvis, open Google in my browser
Command: List all files on my Desktop
Command: Fetch the top 3 Hacker News headlines
Command: Open Spotify
Command: /switch cloud       ← switch to Gemini
Command: /switch local       ← switch to Ollama
Command: /clear              ← clear conversation history
Command: die                 ← shut Jarvis down
```

---

## 🔁 Dual Brain Modes

| Mode | Model | Requires |
|------|-------|----------|
| ☁️ Cloud | Google Gemini | `GEMINI_API_KEY` in `.env` |
| 🖥️ Local | Ollama (LLaMA3, Mistral) | [Ollama](https://ollama.com) installed locally |

Switch anytime mid-conversation with `/switch cloud` or `/switch local`.

---

## 🔐 Safety

Every terminal command or Python script Jarvis wants to run requires **explicit user confirmation** (`y/n`) before execution. Jarvis never runs anything autonomously without your approval.

---

## 🛣️ Roadmap

- [ ] Voice input via OpenAI Whisper
- [ ] Text-to-speech output via `pyttsx3`
- [ ] Web scraping agent (BeautifulSoup + Selenium)
- [ ] Memory/persistent context between sessions
- [ ] GUI interface

---

## 👨‍💻 Author

**Divyarajsinh Chudasama**  
[Portfolio](https://divyaraj-portfolio-1.netlify.app/) • [LinkedIn](https://www.linkedin.com/in/divyarajsinh-chudasama-250b19319/) • [GitHub](https://github.com/Divyaraj94)
