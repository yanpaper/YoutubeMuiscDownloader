#!/usr/bin/env python3
"""
YouTube Playlist to MP3 Downloader

YouTube 플레이리스트 URL을 입력받아 모든 동영상을 MP3 파일로 다운로드합니다.
yt-dlp 라이브러리를 사용합니다.

사용법:
    python youtube_playlist_to_mp3.py "https://www.youtube.com/playlist?list=PLAYLIST_ID"
    python youtube_playlist_to_mp3.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" --output-dir ./music
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path


# 스크립트 디렉토리 (로컬 ffmpeg.exe 위치)
SCRIPT_DIR = Path(__file__).parent.absolute()
LOCAL_FFMPEG = SCRIPT_DIR / "ffmpeg.exe"


def get_ffmpeg_path():
    """사용 가능한 ffmpeg 경로 반환 (로컬 우선, 없으면 PATH에서 찾기)"""
    if LOCAL_FFMPEG.exists():
        return str(LOCAL_FFMPEG)
    return "ffmpeg"


def check_ffmpeg():
    """ffmpeg가 설치되어 있는지 확인 (로컬 포함)"""
    ffmpeg_path = get_ffmpeg_path()
    try:
        subprocess.run([ffmpeg_path, '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_yt_dlp_cmd():
    """yt-dlp 실행 명령어 반환 (PATH에 없을 경우 python -m yt_dlp 사용)"""
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        return ['yt-dlp']
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ['python', '-m', 'yt_dlp']


def get_env_with_local_ffmpeg():
    """로컬 ffmpeg가 있는 경우 PATH에 추가한 환경변수 반환"""
    env = os.environ.copy()
    if LOCAL_FFMPEG.exists():
        # 스크립트 디렉토리를 PATH 앞에 추가
        env['PATH'] = f"{SCRIPT_DIR}{os.pathsep}{env.get('PATH', '')}"
    return env


def download_playlist_to_mp3(playlist_url, output_dir, audio_quality=0, use_android_client=False, cookies=None):
    """
    YouTube 플레이리스트를 MP3로 다운로드
    
    Args:
        playlist_url: YouTube 플레이리스트 URL
        output_dir: 출력 디렉토리
        audio_quality: 오디오 품질 (0=최고, 9=최저)
        use_android_client: Android 클라이언트 사용 (403 우회)
        cookies: 쿠키 파일 경로
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # yt-dlp 명령어 구성
    # -x: 오디오만 추출
    # --audio-format mp3: MP3 포맷으로 변환
    # --audio-quality: 오디오 품질 설정 (0=최고, 9=최저)
    # -o: 출력 파일명 템플릿
    # --embed-thumbnail: 썸네일 임베드
    # --add-metadata: 메타데이터 추가
    # --ignore-errors: 개별 비디오 오류 무시하고 계속 진행
    yt_dlp_cmd = get_yt_dlp_cmd()
    cmd = yt_dlp_cmd + [
        '-x',  # 오디오만 추출
        '--audio-format', 'mp3',
        '--audio-quality', str(audio_quality),
        '--embed-thumbnail',
        '--add-metadata',
        '--ignore-errors',
        '-o', str(output_path / '%(title)s.%(ext)s'),
    ]
    
    # 403 Forbidden 우회 옵션
    if use_android_client:
        cmd += ['--extractor-args', 'youtube:player_client=android']
    
    if cookies:
        cmd += ['--cookies', cookies]
    
    cmd.append(playlist_url)
    
    # 로컬 ffmpeg 사용을 위한 환경변수
    env = get_env_with_local_ffmpeg()
    ffmpeg_info = " (로컬 ffmpeg 사용)" if LOCAL_FFMPEG.exists() else ""
    
    print(f"플레이리스트 다운로드 시작: {playlist_url}")
    print(f"출력 디렉토리: {output_path.absolute()}")
    print(f"오디오 품질: {audio_quality} (0=최고){ffmpeg_info}")
    if use_android_client:
        print("Android 클라이언트 모드 활성화 (403 우회)")
    print("-" * 50)
    
    try:
        # 실시간 출력 확인을 위해 subprocess.run 사용
        result = subprocess.run(cmd, check=True, env=env)
        print("-" * 50)
        print("다운로드 완료!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n다운로드 중 오류 발생: {e}")
        return False
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
        return False


def get_playlist_info(playlist_url):
    """플레이리스트 정보만 가져오기 (다운로드하지 않음)"""
    yt_dlp_cmd = get_yt_dlp_cmd()
    cmd = yt_dlp_cmd + [
        '--flat-playlist',
        '--print', '%(playlist_index)s. %(title)s [%(duration_string)s]',
        playlist_url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"플레이리스트 정보 가져오기 실패: {e}")
        return None


def get_playlist_title(playlist_url):
    """플레이리스트 제목만 가져오기"""
    yt_dlp_cmd = get_yt_dlp_cmd()
    cmd = yt_dlp_cmd + [
        '--flat-playlist',
        '--print', '%(playlist_title)s',
        playlist_url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        title = result.stdout.strip().split('\n')[0]  # 첫 줄만 사용
        # 윈도우에서 사용할 수 없는 문자 제거
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
        return title if title else "Unknown_Playlist"
    except subprocess.CalledProcessError as e:
        print(f"플레이리스트 제목 가져오기 실패: {e}")
        return "Unknown_Playlist"


def main():
    parser = argparse.ArgumentParser(
        description='YouTube 플레이리스트를 MP3 파일로 다운로드',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python youtube_playlist_to_mp3.py "https://www.youtube.com/playlist?list=PLxxx"
  python youtube_playlist_to_mp3.py "https://www.youtube.com/playlist?list=PLxxx" -o ./my_music
  python youtube_playlist_to_mp3.py "https://www.youtube.com/playlist?list=PLxxx" --quality 0 --list-only
        """
    )
    
    parser.add_argument('url', help='YouTube 플레이리스트 URL')
    parser.add_argument('-o', '--output-dir', default='./downloads', 
                        help='출력 디렉토리 (기본값: ./downloads)')
    parser.add_argument('-q', '--quality', type=int, default=0, choices=range(10),
                        help='오디오 품질 0-9 (0=최고, 9=최저, 기본값: 0)')
    parser.add_argument('--list-only', action='store_true',
                        help='플레이리스트 항목만 나열하고 다운로드하지 않음')
    parser.add_argument('--no-thumbnail', action='store_true',
                        help='썸네일 임베드 안 함')
    parser.add_argument('--no-metadata', action='store_true',
                        help='메타데이터 추가 안 함')
    parser.add_argument('--android', action='store_true',
                        help='Android 클라이언트 사용 (403 Forbidden 우회)')
    parser.add_argument('--cookies', type=str,
                        help='브라우저 쿠키 파일 경로 (로그인 필요 시)')
    parser.add_argument('--use-playlist-title', action='store_true', default=True,
                        help='출력 폴더명을 플레이리스트 제목으로 사용 (기본값: 켜짐)')
    parser.add_argument('--no-playlist-title', action='store_false', dest='use_playlist_title',
                        help='출력 폴더명을 플레이리스트 제목으로 사용 안 함')
    
    args = parser.parse_args()
    
    # 플레이리스트 정보만 보기 (ffmpeg 불필요)
    if args.list_only:
        print(f"플레이리스트 정보 가져오는 중: {args.url}")
        print("-" * 50)
        info = get_playlist_info(args.url)
        if info:
            print(info)
        else:
            print("플레이리스트 정보를 가져올 수 없습니다.")
        return
    
    # 출력 디렉토리 결정: 사용자가 지정하지 않았고 --use-playlist-title이 켜져 있으면 플레이리스트 제목 사용
    output_dir = args.output_dir
    if output_dir == './downloads' and args.use_playlist_title:
        print("플레이리스트 제목 가져오는 중...")
        playlist_title = get_playlist_title(args.url)
        output_dir = f"./{playlist_title}"
        print(f"출력 폴더: {output_dir}")
    
    # ffmpeg 확인 (다운로드 시에만 필요)
    if not check_ffmpeg():
        print("⚠️  경고: ffmpeg가 설치되어 있지 않습니다.")
        print("   MP3 변환을 위해 ffmpeg가 필요합니다.")
        print("   Windows: winget install ffmpeg 또는 https://ffmpeg.org/download.html")
        print("   Mac: brew install ffmpeg")
        print("   Linux: sudo apt install ffmpeg")
        print()
        response = input("계속하시겠습니까? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # 다운로드 실행
    success = download_playlist_to_mp3(args.url, output_dir, args.quality, 
                                       use_android_client=args.android, cookies=args.cookies)
    
    if success:
        print(f"\n✅ 완료! 파일들은 '{os.path.abspath(output_dir)}'에 저장되었습니다.")
    else:
        print("\n❌ 다운로드 실패")
        sys.exit(1)


if __name__ == '__main__':
    main()