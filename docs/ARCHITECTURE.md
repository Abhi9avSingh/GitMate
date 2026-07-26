# GitMate Architecture

GitMate is organised as a set of small, single-responsibility modules. Data
flows in one direction: **watchers → service → engine → git/ai → notifier**.

```
GitMate/
├── app/
│   ├── ai/            # AI provider abstraction + commit-message generation
│   │   ├── provider.py         # AIProvider, OpenAIProvider, build_provider()
│   │   ├── commit_generator.py # diff → clean Conventional-Commit line
│   │   └── prompts.py          # system + user prompt templates
│   ├── config/        # Settings dataclass + JSON/keyring persistence
│   ├── core/          # GitMateEngine — the orchestration pipeline
│   ├── git/           # RepositoryManager, DiffFilter, DiffManager,
│   │                  #   CommitManager, PushManager
│   ├── logger/        # rotating file + console logging
│   ├── notifications/ # cross-platform desktop notifications
│   ├── services/      # GitMateService — wires watchers to the engine
│   ├── tray/          # pystray system-tray UI
│   ├── watcher/       # VSCodeWatcher (psutil) + FileWatcher (watchdog)
│   └── utils/         # small shared helpers
├── assets/            # tray icon assets
├── docs/              # documentation
├── tests/             # pytest suite (offline, uses local bare remote)
├── installer/         # PyInstaller spec
├── main.py            # entry point (tray / --once / --status)
└── requirements.txt
```

## The pipeline (`app/core/engine.py`)

```
GitMateEngine.sync()
  1. RepositoryManager.has_changes()   → push protection (skip if clean)
  2. DiffManager.relevant_files()      → DiffFilter removes noise
  3. DiffManager.ai_ready_diff()       → capped, per-file diff (≤ 25 KB)
  4. CommitMessageGenerator.generate() → AI, with deterministic fallback
  5. CommitManager.commit()            → git add -A + git commit
  6. PushManager.push()                → push with retry protection
  7. Notifier.success()/error()        → toast + log
```

## Separation of concerns

| Module            | Does                              | Never does            |
|-------------------|-----------------------------------|-----------------------|
| RepositoryManager | read state, list changes          | commit / push / diff  |
| DiffFilter        | decide which files matter         | run git               |
| DiffManager       | build diffs                       | commit / push / stage |
| CommitManager     | stage + commit                    | push                  |
| PushManager       | push (+ retries)                  | commit                |
| CommitGenerator   | diff → message                    | git operations        |

This makes each piece independently testable — the whole suite runs with **no
network and no real GitHub account** by pushing into a local bare repository.

## Extensibility

- **New AI backends**: implement `AIProvider.complete()` and register it in
  `build_provider()`.
- **New triggers**: add a watcher exposing `start()`/`stop()` and wire it up in
  `GitMateService`.
- **New ignore rules**: extend `DiffFilter` (dirs / extensions / size).

## Roadmap (from the original spec)

- AI-generated `CHANGELOG.md` every 20 commits
- Weekly summary (commits, most-modified folder, top feature, bug fixes)
- Daily pre-push backup archive
- Performance dashboard (commit/push counts, AI latency, uptime)
