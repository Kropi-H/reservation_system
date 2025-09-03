# Cross-platform build script pro ReservationSystem (PowerShell verze)
# Podporuje: Windows, Linux (přes WSL), macOS (přes PowerShell Core)

Write-Host "🌍 Cross-Platform Build Script pro ReservationSystem" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green

# Detekce OS
$OS = ""
if ($IsWindows -or $env:OS -eq "Windows_NT") {
    $OS = "Windows"
    Write-Host "🪟 Detekován Windows" -ForegroundColor Blue
} elseif ($IsLinux) {
    $OS = "Linux"
    Write-Host "🐧 Detekován Linux" -ForegroundColor Blue
} elseif ($IsMacOS) {
    $OS = "macOS"
    Write-Host "🍎 Detekován macOS" -ForegroundColor Blue
} else {
    Write-Host "❌ Nepodporovaný OS" -ForegroundColor Red
    exit 1
}

# Kontrola Python
Write-Host "📋 Kontroluji Python..." -ForegroundColor Yellow
$pythonCmd = "python"
if ($OS -ne "Windows") {
    $pythonCmd = "python3"
}

try {
    & $pythonCmd --version | Out-Null
    Write-Host "✅ Python nalezen" -ForegroundColor Green
} catch {
    Write-Host "❌ Python není nainstalován" -ForegroundColor Red
    if ($OS -eq "Windows") {
        Write-Host "Stáhni Python z https://python.org" -ForegroundColor Yellow
    } else {
        Write-Host "Nainstaluj Python 3.8+" -ForegroundColor Yellow
    }
    exit 1
}

# Vytvoř virtuální prostředí
Write-Host "🐍 Vytvářím Python prostředí..." -ForegroundColor Yellow
& $pythonCmd -m venv venv

# Aktivace venv podle OS
if ($OS -eq "Windows") {
    & ".\venv\Scripts\Activate.ps1"
    $pythonPath = ".\venv\Scripts\python.exe"
    $pipPath = ".\venv\Scripts\pip.exe"
} else {
    # Pro Linux/macOS přes PowerShell Core
    & bash -c "source venv/bin/activate"
    $pythonPath = "venv/bin/python"
    $pipPath = "venv/bin/pip"
}

# Nainstaluj závislosti
Write-Host "📥 Instaluji Python závislosti..." -ForegroundColor Yellow
& $pipPath install --upgrade pip
& $pipPath install -r requirements.txt
& $pipPath install pyinstaller

# Test nových modulů
Write-Host "🔍 Testuji nové real-time notifikace moduly..." -ForegroundColor Yellow
$testScript = @"
import sys
try:
    import models.database_listener
    print('✅ database_listener import OK')
except ImportError as e:
    print(f'❌ database_listener import failed: {e}')
    sys.exit(1)

try:
    from views.hlavni_okno import HlavniOkno
    print('✅ HlavniOkno with real-time notifications import OK')
except ImportError as e:
    print(f'❌ HlavniOkno import failed: {e}')
    sys.exit(1)

try:
    from models.ordinace import add_ordinace, update_ordinace_db, remove_ordinace
    print('✅ ordinace notifications import OK')
except ImportError as e:
    print(f'❌ ordinace notifications failed: {e}')
    sys.exit(1)

try:
    from models.doktori import add_doctor, update_doctor, deactivate_doctor, remove_doctor
    print('✅ doktori notifications import OK')
except ImportError as e:
    print(f'❌ doktori notifications failed: {e}')
    sys.exit(1)

print('🎉 Všechny nové moduly pro real-time notifikace fungují!')
"@

$testResult = & $pythonPath -c $testScript
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Test modulů selhal!" -ForegroundColor Red
    exit 1
}

# Build aplikace
Write-Host "🔨 Builduji $OS aplikaci s real-time notifikacemi..." -ForegroundColor Yellow
& $pythonPath -m PyInstaller ReservationSystem.spec

# Zkontroluj výsledek podle OS
if ($OS -eq "Windows") {
    if (Test-Path "dist\ReservationSystem.exe") {
        Write-Host "✅ Windows build úspěšný!" -ForegroundColor Green
        $size = (Get-Item "dist\ReservationSystem.exe").Length / 1MB
        Write-Host "📁 Soubor: $(Get-Location)\dist\ReservationSystem.exe" -ForegroundColor Cyan
        Write-Host "📊 Velikost: $([math]::Round($size, 1)) MB" -ForegroundColor Cyan
        Write-Host "🚀 Spuštění: .\dist\ReservationSystem.exe" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Windows build selhal!" -ForegroundColor Red
        exit 1
    }
} elseif ($OS -eq "Linux") {
    if (Test-Path "dist/ReservationSystem") {
        Write-Host "✅ Linux build úspěšný!" -ForegroundColor Green
        Write-Host "📁 Soubor: $(Get-Location)/dist/ReservationSystem" -ForegroundColor Cyan
        Write-Host "🚀 Spuštění: chmod +x dist/ReservationSystem && ./dist/ReservationSystem" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Linux build selhal!" -ForegroundColor Red
        exit 1
    }
} elseif ($OS -eq "macOS") {
    if (Test-Path "dist/ReservationSystem.app") {
        Write-Host "✅ macOS build úspěšný!" -ForegroundColor Green
        Write-Host "📁 Aplikace: $(Get-Location)/dist/ReservationSystem.app" -ForegroundColor Cyan
        Write-Host "🚀 Instalace: cp -r dist/ReservationSystem.app /Applications/" -ForegroundColor Yellow
    } else {
        Write-Host "❌ macOS build selhal!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🎉 Build dokončen! Aplikace obsahuje:" -ForegroundColor Green
Write-Host "   ✅ Real-time synchronizaci rezervací" -ForegroundColor Green
Write-Host "   ✅ Real-time synchronizaci doktorů" -ForegroundColor Green
Write-Host "   ✅ Real-time synchronizaci ordinací" -ForegroundColor Green
Write-Host "   ✅ Multi-instance notifikace" -ForegroundColor Green
Write-Host "   ✅ PostgreSQL NOTIFY/LISTEN systém" -ForegroundColor Green
