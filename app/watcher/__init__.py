"""GitMate watcher package.

Provides the two triggers GitMate reacts to:

- ``VSCodeWatcher``  - detects when the editor is closed (via psutil).
- ``FileWatcher``    - detects file changes in the repository (via watchdog).
"""

from __future__ import annotations

from app.watcher.file_watcher import FileWatcher
from app.watcher.vscode_watcher import VSCodeWatcher

__all__ = ["VSCodeWatcher", "FileWatcher"]
