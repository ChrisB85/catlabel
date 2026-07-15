[CmdletBinding()]
param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$buildEnvironment = Join-Path $PSScriptRoot ".launcher-build"
$buildPython = Join-Path $buildEnvironment "Scripts\python.exe"

if (-not (Test-Path -LiteralPath $buildPython)) {
    & $Python -m venv $buildEnvironment
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create the launcher build environment."
    }
}

& $buildPython -m pip install --disable-pip-version-check --requirement launcher-requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install the pinned launcher build dependencies."
}

& $buildPython -m PyInstaller --clean --noconfirm CatLabel-Launcher.spec
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed to build CatLabel-Launcher.exe."
}

$launcher = Join-Path $PSScriptRoot "dist\CatLabel-Launcher.exe"
if (-not (Test-Path -LiteralPath $launcher)) {
    throw "PyInstaller completed without producing $launcher."
}

$hash = Get-FileHash -LiteralPath $launcher -Algorithm SHA256
Write-Host "Built $launcher"
Write-Host "SHA256 $($hash.Hash.ToLowerInvariant())"
