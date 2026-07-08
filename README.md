# GitMate
For the lazy peoples who dont want to push their codes daily 
# GitMate 🚀

> **An AI-powered Git assistant that automatically generates meaningful commit messages and streamlines your Git workflow.**

GitMate monitors your project for file changes, analyzes Git diffs, generates intelligent commit messages using AI, and performs Git operations with minimal developer intervention.

---

## ✨ Features

* 🔍 Automatically detects repository changes
* 📄 Generates Git diffs for modified files
* 🤖 AI-powered commit message generation
* 📝 Supports Conventional Commits
* ⚡ Automatic staging and committing
* ☁️ Push commits to remote repositories
* 🖥️ Monitors repository activity in real time
* ⏳ Debounces frequent file saves using an idle timer
* 🔌 Modular AI provider architecture
* 🧩 Clean, scalable, and extensible design

---

# Project Structure

```text
GitMate/
│
├── app/
│   ├── ai/
│   │   ├── providers/
│   │   └── prompts/
│   │
│   ├── config/
│   ├── core/
│   ├── git/
│   │   ├── repository.py
│   │   ├── diff_manager.py
│   │   ├── commit_manager.py
│   │   └── push_manager.py
│   │
│   ├── logger/
│   ├── notifications/
│   ├── services/
│   ├── tray/
│   ├── utils/
│   │
│   └── watcher/
│       ├── repo_monitor.py
│       ├── idle_timer.py
│       └── vscode_monitor.py
│
├── assets/
├── docs/
├── installer/
├── tests/
│
├── main.py
├── requirements.txt
└── README.md
```

---

# Architecture

```text
Developer
     │
     ▼
Repository Monitor
     │
     ▼
Idle Timer
     │
     ▼
Repository
     │
     ▼
Diff Manager
     │
     ▼
AI Provider
     │
     ▼
Commit Manager
     │
     ▼
Push Manager
     │
     ▼
Git Repository
```

---

# Supported AI Providers

GitMate is designed with a provider-based architecture.

Current and planned providers include:

* Google Gemini
* OpenAI
* Ollama (Local LLMs)

Adding a new provider only requires implementing the provider interface.

---

# Technologies Used

* Python 3.11+
* GitPython
* Watchdog
* Psutil
* Google Gemini API
* OpenAI API (optional)
* Ollama (optional)
* python-dotenv

---

# Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/GitMate.git
```

Move into the project directory:

```bash
cd GitMate
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Configuration

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_api_key
OPENAI_API_KEY=your_api_key
```

Only the providers you intend to use need to be configured.

---

# Current Workflow

```text
File Saved
     │
     ▼
Repository Monitor detects changes
     │
     ▼
Idle Timer waits for inactivity
     │
     ▼
Git Diff generated
     │
     ▼
AI generates commit message
     │
     ▼
Changes staged
     │
     ▼
Commit created
     │
     ▼
Push to remote repository
```

---

# Roadmap

 

* Repository Management
* Diff Generation
* Commit Manager
* Push Manager
* Repository Watcher
* Idle Timer
* VS Code Monitor

 

* Gemini Integration
* Prompt Templates
* Application Orchestrator
* Logging
* Notifications
 

* VS Code Extension
* System Tray Support
* Configuration UI
* Installer
* Auto Update

---

# Future Improvements

* Multi-repository support
* Branch-aware commit generation
* Interactive commit approval
* Automatic pull before push
* Commit history dashboard
* AI-generated pull request descriptions
* GitHub and GitLab integration

---

# Why GitMate?

Writing meaningful commit messages consistently can interrupt development flow. GitMate automates this process by analyzing your code changes and generating concise, descriptive commit messages, allowing you to focus on writing code instead of describing it.

---

# Contributing

Contributions, feature requests, and bug reports are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push your branch
5. Open a Pull Request

---

# License

This project is licensed under the MIT License.

---

# Author

**Abhinav Singh**

B.Tech Computer Science & Engineering

Pranveer Singh Institute of Technology (PSIT), Kanpur

---

⭐ If you find GitMate useful, consider giving the repository a star.

