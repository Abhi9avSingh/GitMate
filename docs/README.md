# GitMate

**Autonomous AI-powered Git commit & push.**

GitMate runs quietly in your system tray. When you finish working (for example,
when you close VS Code) it waits a few seconds, generates a meaningful
[Conventional Commit](https://www.conventionalcommits.org/) message with AI,
commits, and pushes to GitHub — **without ever touching any other repository on
your system.**

> No prompts. No confirmation dialogs. Just clean, automatic history.

The default AI provider is **Google Gemini** (OpenAI is also supported).

---

## How it works

```
Start OS
   │
GitMate starts (system tray)
   │
You work normally in VS Code
   │
You close VS Code
   │
Wait 15 seconds  (debounce)
   │
Detect changes  →  build AI-ready diff  →  generate commit message
   │
git add .  →  git commit  →  git push
   │
✓ Successfully pushed to GitHub
```

## Key design principles

- **The AI never sees your whole project.** It only receives a cleaned
  `git diff`, capped at 25 KB, with binary/large/ignored files removed.
- **One responsibility per module.** `RepositoryManager` only *reads*;
  committing, pushing, diffing and AI live in their own classes.
- **Push protection.** No changes → no commit. Failed push → retry every
  30 seconds until it succeeds.
- **Secrets stay safe.** The API key is stored in the OS keyring, never in
  plain text on disk.

## Installation

```bash
git clone <your-fork> gitmate
cd gitmate
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

GitMate stores config in your user config directory:

- Windows: `%APPDATA%\GitMate\settings.json`
- macOS/Linux: `~/.config/GitMate/settings.json`

Example `settings.json` (Gemini, the default):

```json
{
  "repository_path": "D:/Projects/WeatherApp",
  "branch": "main",
  "remote": "origin",
  "ai_provider": "gemini",
  "ai_model": "gemini-1.5-flash",
  "debounce_seconds": 15,
  "push_retry_interval": 30,
  "watch_editor_process": "Code",
  "start_with_os": true
}
```

### Using Google Gemini (default)

1. Get a free API key at <https://aistudio.google.com/app/apikey>.
2. Make sure `"ai_provider": "gemini"` in `settings.json`
   (models: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-2.0-flash`, ...).
3. Provide the key via an environment variable (or the OS keyring):

```bash
export GEMINI_API_KEY="your-key"      # macOS/Linux (GOOGLE_API_KEY also works)
setx GEMINI_API_KEY "your-key"        # Windows (reopen the terminal after)
```

### Using OpenAI instead (optional)

1. `pip install openai`
2. Set `"ai_provider": "openai"` and e.g. `"ai_model": "gpt-4o-mini"`.
3. `export OPENAI_API_KEY="sk-..."`

> If no key is found, GitMate still works and falls back to a deterministic
> (non-AI) commit message.

## Usage

```bash
python main.py            # launch the tray app
python main.py --once     # run a single commit + push and exit
python main.py --status   # print repository status
python main.py --repo D:/Projects/WeatherApp --once
python main.py --once --no-push   # commit only
```

## Tray menu

```
GitMate
● Watching
Repository: WeatherApp
Last Push: 2 minutes ago
───────────────
Push Now
Open Logs
Settings
Exit
```

## Development

```bash
pip install -r requirements-dev.txt
pytest            # run the test-suite (no network needed)
black app tests   # format
mypy app          # type-check
```

## Building a Windows .exe

```bash
pip install pyinstaller
pyinstaller installer/gitmate.spec
# → dist/GitMate.exe
```

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for a module-by-module breakdown.

## License

MIT © Aachman Dixit
