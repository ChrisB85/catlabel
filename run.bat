@echo off
setlocal EnableExtensions DisableDelayedExpansion
title CatLabel Bootstrapper

cd /d "%~dp0"
if errorlevel 1 goto error_workdir

set "SETUP_ONLY=0"
set "INSTALL_HEADLESS=0"
set "SKIP_HEADLESS=0"

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--setup-only" goto arg_setup_only
if /I "%~1"=="--install-headless" goto arg_install_headless
if /I "%~1"=="--skip-headless" goto arg_skip_headless
echo ERROR: Unknown option: %~1
goto error_usage

:arg_setup_only
set "SETUP_ONLY=1"
shift
goto parse_args

:arg_install_headless
set "INSTALL_HEADLESS=1"
shift
goto parse_args

:arg_skip_headless
set "SKIP_HEADLESS=1"
shift
goto parse_args

:args_done
set "PIXI_VERSION=0.72.2"
set "PIXI_SHA256=3f6e03db3cb275c028035ed3975180198064d8bb6d0352b5ab958c1fcfbddc4e"
set "PIXI_URL=https://github.com/prefix-dev/pixi/releases/download/v%PIXI_VERSION%/pixi-x86_64-pc-windows-msvc.exe"
set "PIXI_EXE=bin\pixi.exe"
set "PIXI_TMP=bin\pixi.exe.download"

rem Keep Pixi's environment, global data, and package cache inside CatLabel.
set "PIXI_HOME=%cd%\data\pixi_home"
set "PIXI_CACHE_DIR=%cd%\data\pixi_cache"
set "PIXI_NO_CONFIG=1"
set "CATLABEL_DOWNLOAD_URL=%PIXI_URL%"
set "CATLABEL_DOWNLOAD_PATH=%cd%\%PIXI_TMP%"

if not exist "bin" mkdir "bin"
if errorlevel 1 goto error_create_dirs
if not exist "data" mkdir "data"
if errorlevel 1 goto error_create_dirs

echo === CatLabel Bootstrapper ===
echo.
echo [1/3] Checking portable Pixi %PIXI_VERSION%...

if not exist "%PIXI_EXE%" goto download_pixi
set "INSTALLED_PIXI_VERSION="
for /f "tokens=2" %%V in ('bin\pixi.exe --version 2^>nul') do set "INSTALLED_PIXI_VERSION=%%V"
if /I not "%INSTALLED_PIXI_VERSION%"=="%PIXI_VERSION%" goto replace_pixi
echo       Pixi is ready.
goto pixi_ready

:replace_pixi
echo       Replacing missing, damaged, or outdated Pixi executable...
del /Q "%PIXI_EXE%" 2>nul

:download_pixi
echo       Downloading the standalone Pixi executable...
del /Q "%PIXI_TMP%" 2>nul
where curl.exe >nul 2>nul
if errorlevel 1 goto download_pixi_powershell
curl.exe --fail --location --retry 3 --retry-delay 2 --connect-timeout 30 --output "%PIXI_TMP%" "%PIXI_URL%"
if errorlevel 1 goto error_download
goto verify_pixi

:download_pixi_powershell
echo       curl.exe was not found; using Windows PowerShell instead...
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing -Uri $env:CATLABEL_DOWNLOAD_URL -OutFile $env:CATLABEL_DOWNLOAD_PATH"
if errorlevel 1 goto error_download

:verify_pixi
echo       Verifying Pixi checksum...
set "DOWNLOADED_PIXI_SHA256="
for /f %%H in ('powershell.exe -NoLogo -NoProfile -NonInteractive -Command "(Get-FileHash -LiteralPath $env:CATLABEL_DOWNLOAD_PATH -Algorithm SHA256).Hash.ToLowerInvariant()"') do set "DOWNLOADED_PIXI_SHA256=%%H"
if not defined DOWNLOADED_PIXI_SHA256 goto error_checksum
if /I not "%DOWNLOADED_PIXI_SHA256%"=="%PIXI_SHA256%" goto error_checksum
move /Y "%PIXI_TMP%" "%PIXI_EXE%" >nul
if errorlevel 1 goto error_download

set "INSTALLED_PIXI_VERSION="
for /f "tokens=2" %%V in ('bin\pixi.exe --version 2^>nul') do set "INSTALLED_PIXI_VERSION=%%V"
if /I not "%INSTALLED_PIXI_VERSION%"=="%PIXI_VERSION%" goto error_pixi
echo       Pixi downloaded and verified.

:pixi_ready
set "PIXI_ENV=default"
if exist "data\.headless-enabled" set "PIXI_ENV=headless"
if "%INSTALL_HEADLESS%"=="1" set "PIXI_ENV=headless"

set "FIRST_INSTALL=0"
if not exist ".pixi\envs\%PIXI_ENV%\python.exe" set "FIRST_INSTALL=1"

echo [2/3] Synchronizing the locked CatLabel environment ^(%PIXI_ENV%^)...
"%PIXI_EXE%" install --environment "%PIXI_ENV%" --locked
if errorlevel 1 goto error_install

if exist ".update_needed" del /Q ".update_needed" 2>nul

if /I "%PIXI_ENV%"=="headless" goto ensure_headless_browser
if "%FIRST_INSTALL%"=="0" goto setup_complete
if exist "data\.headless-skipped" goto setup_complete
if "%SKIP_HEADLESS%"=="1" goto mark_headless_skipped

echo [3/3] Optional headless browser support
echo       This is only needed for third-party API rendering and downloads Chromium.
choice /C YN /T 15 /D N /M "Install headless API support? (Auto-skipping in 15s)"
if errorlevel 2 goto mark_headless_skipped
goto install_headless

:mark_headless_skipped
> "data\.headless-skipped" echo 1
echo       Skipping optional headless browser support.
goto setup_complete

:install_headless
set "PIXI_ENV=headless"
echo [3/3] Installing optional headless environment...
"%PIXI_EXE%" install --environment "headless" --locked
if errorlevel 1 goto error_install

:ensure_headless_browser
echo [3/3] Checking optional headless Chromium installation...
set "PLAYWRIGHT_BROWSERS_PATH=0"
"%PIXI_EXE%" run --environment "headless" --locked python -m playwright install chromium
if errorlevel 1 goto error_headless
> "data\.headless-enabled" echo 1
if exist "data\.headless-skipped" del /Q "data\.headless-skipped" 2>nul

:setup_complete
echo.
echo Installation is synchronized and ready.
echo -----------------------------------
if "%SETUP_ONLY%"=="1" exit /b 0

if not defined CATLABEL_PORT set "CATLABEL_PORT=8000"
echo Starting CatLabel Server (http://localhost:%CATLABEL_PORT%)...
set "PLAYWRIGHT_BROWSERS_PATH=0"
"%PIXI_EXE%" run --environment "%PIXI_ENV%" --locked python -m catlabel
set "APP_EXIT_CODE=%ERRORLEVEL%"
if "%APP_EXIT_CODE%"=="0" exit /b 0
goto error_server

:error_usage
echo Usage: run.bat [--setup-only] [--install-headless ^| --skip-headless]
call :maybe_pause
exit /b 2

:error_workdir
echo ERROR: Failed to switch to the CatLabel installation directory.
call :maybe_pause
exit /b 3

:error_create_dirs
echo ERROR: Failed to create CatLabel's local bin or data directory.
echo Move CatLabel to a folder where your Windows account has write access.
call :maybe_pause
exit /b 4

:error_download
del /Q "%PIXI_TMP%" 2>nul
echo ERROR: Failed to download Pixi after multiple attempts.
echo Check your internet connection, proxy, firewall, and GitHub access, then retry.
call :maybe_pause
exit /b 5

:error_checksum
del /Q "%PIXI_TMP%" 2>nul
echo ERROR: The downloaded Pixi executable failed checksum verification.
echo No unverified executable was run. Please retry the download.
call :maybe_pause
exit /b 6

:error_pixi
echo ERROR: Pixi could not be started after download.
call :maybe_pause
exit /b 7

:error_install
echo ERROR: Pixi could not synchronize the locked CatLabel environment.
echo Re-run this launcher to retry; Pixi safely resumes partial installations.
call :maybe_pause
exit /b 8

:error_headless
echo ERROR: Optional Chromium installation failed.
echo CatLabel itself is installed. Retry with: run.bat --install-headless
call :maybe_pause
exit /b 9

:error_server
echo ERROR: The CatLabel server exited with code %APP_EXIT_CODE%.
call :maybe_pause
exit /b %APP_EXIT_CODE%

:maybe_pause
if "%SETUP_ONLY%"=="1" exit /b 0
pause
exit /b 0
