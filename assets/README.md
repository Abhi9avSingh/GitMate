# Assets

Place the tray icon here.

- `gitmate.ico` — Windows icon used by the PyInstaller build
  (`installer/gitmate.spec`).

At runtime, if no `.ico` is present, `app/tray/tray_app.py` draws a simple
round icon with Pillow, so the app still runs without a bundled asset.
