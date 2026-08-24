@echo off
chcp 65001 >nul
echo ========================================
echo YouTube Playlist to MP3 Downloader
echo ========================================
echo.

REM Argument handling
set "playlist_url="
set "outdir=downloads"

if "%~1"=="" (
    echo Usage: download_playlist.bat "YouTube_Playlist_URL" [output_folder]
    echo.
    echo Examples:
    echo   download_playlist.bat "https://www.youtube.com/playlist?list=PLxxx"
    echo   download_playlist.bat "https://www.youtube.com/playlist?list=PLxxx" "C:\Music"
    echo.
    set /p "playlist_url=Enter playlist URL: "
    if "%playlist_url%"=="" (
        echo No URL entered.
        pause
        exit /b 1
    )
    
    set /p "outdir=Output folder (default: downloads): "
    if "%outdir%"=="" set "outdir=downloads"
) else (
    set "playlist_url=%~1"
    if not "%~2"=="" set "outdir=%~2"
)

echo.
echo Playlist: %playlist_url%
echo Output folder: %outdir%
echo.

python youtube_playlist_to_mp3.py "%playlist_url%" -o "%outdir%" --android --auto-install-ffmpeg

echo.
pause