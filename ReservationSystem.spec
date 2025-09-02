# -*- mode: python ; coding: utf-8 -*-
import sys
import os

# Detect platform for icon handling
is_windows = sys.platform.startswith('win')
is_macos = sys.platform == 'darwin'
is_linux = sys.platform.startswith('linux')

# Set icon path based on platform
icon_path = None
if is_windows:
    icon_path = 'pictures/karakal_logo_grey.ico'
elif is_macos:
    # For macOS, we'll need to create icns file first
    icon_path = 'pictures/karakal_logo_grey.icns'
# Linux: ikona se nastavuje přes .desktop soubor, ne PyInstaller

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'), 
        ('pictures', 'pictures'),
        ('chat', 'chat'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets', 
        'PySide6.QtGui',
        'PySide6.QtSql',
        'PySide6.QtNetwork',
        'psycopg2',
        'psycopg2._psycopg',
        'psycopg2.extensions',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ReservationSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False if (is_windows or is_macos) else True,  # GUI na Windows/macOS, console na Linux
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,  # Will be None on Linux, which is correct
)

# macOS app bundle (only on macOS)
if is_macos:
    app = BUNDLE(
        exe,
        name='ReservationSystem.app',
        icon=icon_path,
        bundle_identifier='com.karakal.reservationsystem',
    )
