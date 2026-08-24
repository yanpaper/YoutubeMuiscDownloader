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
import platform
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path


# 스크립트 디렉토리 (로컬 ffmpeg.exe 위치)
SCRIPT_DIR = Path(__file__).parent.absolute()
LOCAL_FFMPEG = SCRIPT_DIR / "ffmpeg.exe"


def get_ffmpeg_path():
    """사용 가능한 ffmpeg 경로 반환 (로컬 우선, 없으면 PATH에서 찾기)"""
    if LOCAL_FFMPEG.exists():
        return str(LOCAL_FFMPEG)
    return "ffmpeg"


def load_blacklist(blacklist_path):
    """블랙리스트 파일에서 제외할 비디오 ID/URL 로드"""
    blacklist = set()
    if blacklist_path and Path(blacklist_path).exists():
        try:
            with open(blacklist_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 주석과 빈 줄 무시
                    if line and not line.startswith('#'):
                        # URL에서 video ID 추출 또는 전체 URL/ID 그대로 사용
                        if 'youtube.com/watch?v=' in line:
                            video_id = line.split('v=')[1].split('&')[0]
                            blacklist.add(video_id)
                        elif 'youtu.be/' in line:
                            video_id = line.split('youtu.be/')[1].split('?')[0]
                            blacklist.add(video_id)
                        else:
                            # 직접 ID로 입력된 경우
                            blacklist.add(line)
            print(f"블랙리스트 로드: {len(blacklist)}개 항목 ({blacklist_path})")
        except Exception as e:
            print(f"블랙리스트 로드 실패: {e}")
    return blacklist


def check_ffmpeg():
    """ffmpeg가 설치되어 있는지 확인 (로컬 포함)"""
    ffmpeg_path = get_ffmpeg_path()
    try:
        subprocess.run([ffmpeg_path, '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_os_info():
    """OS 정보 반환"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    return system, machine


def download_file(url, dest_path, progress_callback=None):
    """파일 다운로드 (진행률 표시)"""
    def _progress_hook(block_num, block_size, total_size):
        if progress_callback and total_size > 0:
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            progress_callback(percent)
    
    urllib.request.urlretrieve(url, dest_path, _progress_hook)


def install_ffmpeg_windows():
    """Windows에서 ffmpeg 다운로드 및 설치"""
    print("Windows용 ffmpeg 다운로드 중...")
    
    # BtbN/ffmpeg-builds에서 zip 다운로드
    url = "https://github.com/BtbN/ffmpeg-builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    zip_path = SCRIPT_DIR / "ffmpeg_temp.zip"
    
    try:
        print(f"다운로드: {url}")
        download_file(url, zip_path, lambda p: print(f"\r진행률: {p:.1f}%", end="", flush=True))
        print()
        
        print("압축 해제 중...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # ffmpeg.exe 찾기
            for member in zip_ref.namelist():
                if member.endswith('ffmpeg.exe'):
                    # 루트에 추출
                    zip_ref.extract(member, SCRIPT_DIR)
                    extracted = SCRIPT_DIR / member
                    # 파일명 정리 (폴더 구조 평탄화)
                    if extracted != LOCAL_FFMPEG:
                        shutil.move(str(extracted), str(LOCAL_FFMPEG))
                    print(f"✅ ffmpeg.exe 설치 완료: {LOCAL_FFMPEG}")
                    break
        
        # 임시 파일 정리
        zip_path.unlink(missing_ok=True)
        # 빈 폴더 정리
        for item in SCRIPT_DIR.iterdir():
            if item.is_dir() and item.name.startswith('ffmpeg-'):
                shutil.rmtree(item, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ffmpeg 설치 실패: {e}")
        zip_path.unlink(missing_ok=True)
        return False


def install_ffmpeg_linux():
    """Linux에서 패키지 매니저로 ffmpeg 설치"""
    print("Linux 패키지 매니저로 ffmpeg 설치 시도...")
    
    # 패키지 매니저 감지
    package_managers = [
        (['apt', 'install', '-y', 'ffmpeg'], 'apt (Ubuntu/Debian)'),
        (['dnf', 'install', '-y', 'ffmpeg'], 'dnf (Fedora/RHEL)'),
        (['yum', 'install', '-y', 'ffmpeg'], 'yum (CentOS/RHEL)'),
        (['pacman', '-S', '--noconfirm', 'ffmpeg'], 'pacman (Arch)'),
        (['zypper', 'install', '-y', 'ffmpeg'], 'zypper (openSUSE)'),
    ]
    
    for cmd, name in package_managers:
        try:
            # 패키지 매니저 존재 확인
            subprocess.run([cmd[0], '--version'], capture_output=True, check=True)
            print(f"{name} 감지됨, 설치 중...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ ffmpeg 설치 완료")
                return True
            else:
                print(f"{name} 설치 실패: {result.stderr}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    print("❌ 지원되는 패키지 매니저를 찾을 수 없습니다.")
    return False


def install_ffmpeg_macos():
    """macOS에서 Homebrew로 ffmpeg 설치"""
    print("macOS Homebrew로 ffmpeg 설치 시도...")
    
    try:
        subprocess.run(['brew', '--version'], capture_output=True, check=True)
        print("Homebrew 감지됨, 설치 중...")
        result = subprocess.run(['brew', 'install', 'ffmpeg'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ffmpeg 설치 완료")
            return True
        else:
            print(f"Homebrew 설치 실패: {result.stderr}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Homebrew가 설치되어 있지 않습니다.")
    
    return False


def auto_install_ffmpeg(interactive=True):
    """OS 감지 후 ffmpeg 자동 설치"""
    if check_ffmpeg():
        return True
    
    system, machine = get_os_info()
    print(f"\n🔍 OS 감지: {system} ({machine})")
    print("ffmpeg가 설치되어 있지 않습니다.")
    
    if interactive:
        response = input("자동으로 설치하시겠습니까? (Y/n): ").strip().lower()
        if response == 'n':
            return False
    else:
        print("자동 설치 모드: ffmpeg 설치 진행...")
    
    success = False
    
    if system == 'windows':
        success = install_ffmpeg_windows()
    elif system == 'linux':
        success = install_ffmpeg_linux()
    elif system == 'darwin':
        success = install_ffmpeg_macos()
    else:
        print(f"지원하지 않는 OS: {system}")
        return False
    
    if success:
        # 설치 후 재확인
        if check_ffmpeg():
            print("✅ ffmpeg 설치 및 확인 완료!")
            return True
        else:
            print("❌ 설치되었으나 ffmpeg를 찾을 수 없습니다.")
            return False
    else:
        print("❌ 자동 설치 실패. 수동으로 설치해주세요.")
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


def download_playlist_to_mp3(playlist_url, output_dir, audio_quality=0, use_android_client=False, cookies=None, blacklist=None):
    """
    YouTube 플레이리스트를 MP3로 다운로드
    
    Args:
        playlist_url: YouTube 플레이리스트 URL
        output_dir: 출력 디렉토리
        audio_quality: 오디오 품질 (0=최고, 9=최저)
        use_android_client: Android 클라이언트 사용 (403 우회)
        cookies: 쿠키 파일 경로
        blacklist: 제외할 비디오 ID 집합
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 블랙리스트가 있으면 yt-dlp의 --match-filter로 필터링
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
    
    # 블랙리스트 필터링 (video ID 기준)
    if blacklist:
        # yt-dlp의 match_filter 사용: video_id가 블랙리스트에 없으면 다운로드
        filter_expr = " and ".join([f"id != '{vid}'" for vid in blacklist])
        cmd += ['--match-filter', filter_expr]
        print(f"블랙리스트 필터 적용: {len(blacklist)}개 영상 제외")
    
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
    parser.add_argument('--auto-install-ffmpeg', action='store_true',
                        help='ffmpeg 자동 설치 (OS 감지 후 다운로드/설치)')
    parser.add_argument('--blacklist', type=str, default='blacklist.txt',
                        help='제외할 영상 목록 파일 (기본값: blacklist.txt)')
    parser.add_argument('--no-blacklist', action='store_true',
                        help='블랙리스트 사용 안 함')
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
    
    # ffmpeg 확인 및 자동 설치 (다운로드 시에만 필요)
    if not check_ffmpeg():
        print("⚠️  경고: ffmpeg가 설치되어 있지 않습니다.")
        if args.auto_install_ffmpeg:
            print("자동 설치 모드: OS 감지 후 설치 시도...")
            if not auto_install_ffmpeg(interactive=False):
                print("❌ 자동 설치 실패. 수동으로 설치해주세요.")
                sys.exit(1)
        else:
            print("   MP3 변환을 위해 ffmpeg가 필요합니다.")
            print("   Windows: winget install ffmpeg 또는 https://ffmpeg.org/download.html")
            print("   Mac: brew install ffmpeg")
            print("   Linux: sudo apt install ffmpeg")
            print("   또는 --auto-install-ffmpeg 옵션으로 자동 설치 시도")
            print()
            response = input("계속하시겠습니까? (y/N): ")
            if response.lower() != 'y':
                sys.exit(1)
    
    # 블랙리스트 로드
    blacklist = set()
    if not args.no_blacklist:
        blacklist = load_blacklist(args.blacklist)
    
    # 다운로드 실행
    success = download_playlist_to_mp3(args.url, output_dir, args.quality, 
                                       use_android_client=args.android, cookies=args.cookies,
                                       blacklist=blacklist)
    
    if success:
        print(f"\n✅ 완료! 파일들은 '{os.path.abspath(output_dir)}'에 저장되었습니다.")
    else:
        print("\n❌ 다운로드 실패")
        sys.exit(1)


if __name__ == '__main__':
    main()