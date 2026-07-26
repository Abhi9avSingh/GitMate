# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for building GitMate into a single Windows .exe.

Build with:
    pyinstaller installer/gitmate.spec

The result is a windowed (no console) executable in ``dist/GitMate.exe``.
"""

block_cipher = None


a = Analysis(
    ['..\\main.py'],
    pathex=['..'],
    binaries=[],
    datas=[('..\\assets', 'assets')],
    hiddenimports=[
        'pystray._win32',
        'PIL._tkinter_finder',
        'win10toast',
        'keyring.backends.Windows',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GitMate',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='..\\assets\\gitmate.ico',
)
