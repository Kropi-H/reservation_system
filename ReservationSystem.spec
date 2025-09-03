# -*- mode: python ; coding: utf-8 -*-
import os
import platform

# Detekce platformy pro správné nastavení
PLATFORM = platform.system()
print(f"🔧 Buildování pro platformu: {PLATFORM}")

# Nastavení ikony podle platformy
if PLATFORM == "Darwin":  # macOS
    icon_file = 'pictures/karakal_logo_grey.icns'
elif PLATFORM == "Windows":
    icon_file = 'pictures/karakal_logo_grey.ico'
else:  # Linux
    icon_file = None  # Linux nemá ikonu v .spec

# Kontrola existence ikony
if icon_file and not os.path.exists(icon_file):
    print(f"⚠️ Ikona {icon_file} neexistuje!")
    icon_file = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('pictures', 'pictures'), ('config.json', '.') if os.path.exists('config.json') else None],
    hiddenimports=['asyncio', 'threading', 'psycopg2', 'psycopg2.pool', 'psycopg2.extras', 'sqlalchemy', 'models.database_listener', 'models.connection_pool', 'multiprocessing', 'select', 'queue'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)

# Vytvoření .app bundle pro macOS
if PLATFORM == "Darwin":
    app = BUNDLE(
        exe,
        name='ReservationSystem.app',
        icon=icon_file,
        bundle_identifier='com.karakal.reservationsystem',
    )
