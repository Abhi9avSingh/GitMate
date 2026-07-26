"""
GitMate entry point.
---------------------

Usage
-----
    python main.py                # launch the tray app
    python main.py --once         # run a single commit + push and exit
    python main.py --status       # print repository status and exit
    python main.py --repo PATH    # override the configured repository
    python main.py --no-push      # commit only, do not push (with --once)

GitMate reads its configuration from the user's config directory
(``%APPDATA%/GitMate`` on Windows, ``~/.config/GitMate`` elsewhere). The
OpenAI API key is read from the OS keyring or the ``OPENAI_API_KEY``
environment variable.
"""

from __future__ import annotations

import argparse
import sys

from app import __app_name__, __version__
from app.config.settings import SettingsStore
from app.logger.logger import get_logger, setup_logging
from app.notifications.notifier import Notifier


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="gitmate", description="Autonomous AI-powered Git commit & push."
    )
    parser.add_argument("--version", action="version", version=f"{__app_name__} {__version__}")
    parser.add_argument("--repo", help="Path to the repository (overrides config).")
    parser.add_argument("--once", action="store_true", help="Run one sync and exit.")
    parser.add_argument("--no-push", action="store_true", help="Commit only, skip push.")
    parser.add_argument("--status", action="store_true", help="Print status and exit.")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)
    setup_logging()
    log = get_logger("main")

    store = SettingsStore()
    settings = store.load()
    if args.repo:
        settings.repository_path = args.repo

    if not settings.repository_path:
        log.error(
            "No repository configured. Set 'repository_path' in settings.json "
            "or pass --repo PATH."
        )
        return 2

    # Import here so a missing GUI stack never blocks --once / --status.
    from app.core.engine import GitMateEngine
    from app.services.gitmate_service import GitMateService

    notifier = Notifier(__app_name__)

    try:
        engine = GitMateEngine(settings, notifier)
    except Exception as exc:
        log.error("Could not open repository: %s", exc)
        return 1

    if args.status:
        for key, value in engine.status().items():
            print(f"{key:>15}: {value}")
        return 0

    if args.once:
        result = engine.sync(push=not args.no_push)
        print(result)
        return 0 if not result.error else 1

    service = GitMateService(settings, engine=engine, notifier=notifier)
    try:
        from app.tray.tray_app import TrayApp

        TrayApp(service).run()
    except RuntimeError as exc:
        # No GUI available - fall back to a headless watch loop.
        log.warning("%s Running headless; press Ctrl+C to stop.", exc)
        service.start()
        try:
            import time

            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            service.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
