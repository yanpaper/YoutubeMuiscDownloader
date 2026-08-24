@echo off
chcp 65001 >nul
echo ========================================
echo YouTube Playlist to MP3 Downloader
echo ========================================
echo.

set "playlist_url="
set "outdir=downloads"

REM If first argument is a file, read URL from it
if not "%~1"=="" (
    if exist "%~1" (
        REM Read URL from file (avoids PowerShell ? parsing issues)
        set /p playlist_url=<"%~1"
        if not "%~2"=="" set "outdir=%~2"
        goto :run_download
    )
    
    REM Check if URL is truncated (PowerShell mangles ? and =)
    REM If URL contains "playlist?list" without "list=", it's truncated
    echo %~1 | findstr /C:"playlist?list" >nul
    if not errorlevel 1 (
        echo.
        echo [경고] PowerShell에서 URL 특수문자(?,=)가 잘렸습니다.
        echo.
        echo 해결 방법 1: URL을 파일에 저장 후 실행
        echo   echo https://www.youtube.com/playlist?list=PLxxx > url.txt
        echo   download_playlist.bat url.txt
        echo.
        echo 해결 방법 2: PowerShell에서 --% 토큰 사용
        echo   download_playlist.bat --% "https://www.youtube.com/playlist?list=PLxxx"
        echo.
        echo 해결 방법 3: cmd.exe에서 직접 실행
        echo   cmd /c download_playlist.bat "https://www.youtube.com/playlist?list=PLxxx"
        echo.
        echo 해결 방법 4: Python 직접 실행 (가장 권장)
        echo   python youtube_playlist_to_mp3.py "https://www.youtube.com/playlist?list=PLxxx" --android --auto-install-ffmpeg
        echo.
        pause
        exit /b 1
    )
    
    REM Check if --% token was used (PowerShell stop-parsing)
    if "%~1"=="--%" (
        shift
        set "playlist_url=%~1"
        if not "%~2"=="" set "outdir=%~2"
    ) else (
        set "playlist_url=%~1"
        if not "%~2"=="" set "outdir=%~2"
    )
    goto :run_download
)

REM Interactive mode
echo This tool downloads YouTube playlists as MP3 files.
echo.
echo Enter the playlist URL below (copy & paste):
echo.

set /p "playlist_url=Playlist URL: "
if "%playlist_url%"=="" (
    echo Error: No URL entered.
    pause
    exit /b 1
)

set /p "outdir=Output folder [default: downloads]: "
if "%outdir%"=="" set "outdir=downloads"

:run_download
echo.
echo ----------------------------------------------
echo Playlist: %playlist_url%
echo Output folder: %outdir%
echo ----------------------------------------------
echo.

python youtube_playlist_to_mp3.py "%playlist_url%" -o "%outdir%" --android --auto-install-ffmpeg

echo.
echo ----------------------------------------------
pause