@echo off
REM ============================================================
REM YouTube Playlist to MP3 Downloader
REM PowerShell-friendly (no --% required)
REM ============================================================

REM Switch to UTF-8 codepage for safe Unicode handling
chcp 65001 >nul

set "outdir=downloads"
set "playlist_url="

REM --- Priority 1: YT_URL env var (recommended for PowerShell) ---
REM     PowerShell:  $env:YT_URL = "URL"; .\download_playlist.bat
REM     cmd:         set YT_URL=URL ^&^& download_playlist.bat
if defined YT_URL (
    set "playlist_url=%YT_URL%"
    if defined YT_OUTDIR set "outdir=%YT_OUTDIR%"
    goto :run_download
)

REM --- Priority 2: --% token (PowerShell stop-parsing) ---
if "%~1"=="--%" (
    shift
    set "playlist_url=%~1"
    if not "%~2"=="" set "outdir=%~2"
    goto :run_download
)

REM --- Priority 3: direct argument ---
if not "%~1"=="" (
    set "playlist_url=%~1"
    if not "%~2"=="" set "outdir=%~2"
    goto :run_download
)

REM --- Priority 4: interactive mode ---
echo ========================================
echo YouTube Playlist to MP3 Downloader
echo ========================================
echo.
echo Usage (PowerShell/cmd):
echo   .\download_playlist.bat "https://www.youtube.com/playlist?list=PLxxx"
echo   .\download_playlist.bat "https://www.youtube.com/playlist?list=PLxxx" "C:\Music"
echo.
echo PowerShell tip: use $env:YT_URL to avoid quoting issues
echo   $env:YT_URL = "URL"
echo   .\download_playlist.bat
echo.
set /p "playlist_url=Playlist URL: "
if "%playlist_url%"=="" (
    echo No URL entered.
    pause
    exit /b 1
)
set /p "outdir=Output folder (default: downloads): "
if "%outdir%"=="" set "outdir=downloads"

:run_download
echo.
echo ----------------------------------------------
echo Playlist: %playlist_url%
echo Output folder: %outdir%
echo ----------------------------------------------
echo.

REM Validate URL via Python (use a helper script to avoid quoting issues)
if exist "%~dp0_validate_url.py" (
    python "%~dp0_validate_url.py" "%playlist_url%"
) else (
    python -c "import sys; sys.exit(0 if any(s in sys.argv[1] for s in ('list=','youtu.be/','watch?v=')) else 1)" "%playlist_url%"
)
if %errorlevel% neq 0 goto :bad_url
goto :run_python

:bad_url
echo.
echo [ERROR] URL is invalid or PowerShell stripped special chars.
echo Input: %playlist_url%
echo.
echo Solutions:
echo   1) Use YT_URL env var - recommended for PowerShell:
echo        set YT_URL=URL
echo        download_playlist.bat
echo.
echo   2) Use -- percent token:
echo        download_playlist.bat -- percent "URL"
echo.
echo   3) Run from cmd.exe:
echo        cmd /c download_playlist.bat "URL"
echo.
pause
exit /b 1

:run_python
python youtube_playlist_to_mp3.py "%playlist_url%" -o "%outdir%" --android --auto-install-ffmpeg

echo.
echo ----------------------------------------------
pause