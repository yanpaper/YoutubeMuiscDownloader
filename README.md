# YouTube Playlist to MP3 Downloader

[🇺🇸 English](README_EN.md) | **🇰🇷 한국어**

---

YouTube 플레이리스트의 모든 영상을 MP3 파일로 일괄 다운로드하는 도구입니다.

## ✨ 주요 기능

- 🎵 **플레이리스트 전체 다운로드** - 순서대로 MP3 변환
- 🖼️ **썸네일 임베드** - 앨범 아트 자동 포함
- 🏷️ **메타데이터 추가** - 제목, 아티스트, 앨범 등 태그 자동 입력
- 📁 **플레이리스트 제목으로 폴더 자동 생성** - 깔끔한 정리
- 🔄 **403 Forbidden 우회** - Android 클라이언트 모드 지원
- 🍪 **쿠키 지원** - 비공개/연령제한 영상 다운로드 가능
- ⚡ **로컬 ffmpeg 자동 감지** - 별도 설치 불필요 (폴더에 ffmpeg.exe만 두면 됨)
- 🤖 **ffmpeg 자동 설치** - OS 감지 후 자동 다운로드/설치 (`--auto-install-ffmpeg`)

---

## 📋 필수 준비사항

| 프로그램 | 설치 방법 |
|----------|-----------|
| **Python** | 3.8 이상 권장 |
| **yt-dlp** | `pip install yt-dlp` |
| **ffmpeg** | 프로젝트 폴더에 `ffmpeg.exe` 배치 또는 [공식 사이트](https://ffmpeg.org/download.html)에서 다운로드 후 PATH 추가 |

> **팁:** 이 저장소에는 `ffmpeg.exe`가 포함되어 있지 않습니다. `.gitignore`에 의해 제외됩니다. 직접 다운로드하여 프로젝트 폴더에 두세요.

---

## 🚀 설치 및 사용법

### 1. 저장소 클론
```bash
git clone https://github.com/yanpaper/YoutubeMuiscDownloader.git
cd YoutubeMuiscDownloader
```

### 2. 의존성 설치
```bash
pip install yt-dlp
```

### 3. ffmpeg 배치 (선택사항 - 프로젝트 폴더에 두면 자동 감지)
- [ffmpeg 공식 빌드](https://www.gyan.dev/ffmpeg/builds/)에서 `ffmpeg-essentials_build.zip` 다운로드
- 압축 해제 후 `ffmpeg.exe`를 프로젝트 루트에 복사

---

## 💻 사용법

### Python 직접 실행 (추천 - 모든 옵션 사용 가능)

```bash
# 기본: 플레이리스트 제목으로 폴더 자동 생성 + Android 모드(403 우회)
python youtube_playlist_to_mp3.py "https://www.youtube.com/playlist?list=PLxxx" --android

# 출력 폴더 직접 지정
python youtube_playlist_to_mp3.py "URL" -o ./my_music --android

# 고음질 (0=최고, 9=최저, 기본 0)
python youtube_playlist_to_mp3.py "URL" -q 0 --android

# 플레이리스트 내용만 미리보기 (다운로드 안 함, ffmpeg 불필요)
python youtube_playlist_to_mp3.py "URL" --list-only

# 썸네일 임베드 안 함
python youtube_playlist_to_mp3.py "URL" --no-thumbnail --android

# 메타데이터 추가 안 함
python youtube_playlist_to_mp3.py "URL" --no-metadata --android

# 비공개/연령제한 영상 - 브라우저 쿠키 사용
python youtube_playlist_to_mp3.py "URL" --cookies cookies.txt --android

# 플레이리스트 제목으로 폴더 생성 안 함 (기본 downloads 폴더 사용)
python youtube_playlist_to_mp3.py "URL" --no-playlist-title --android

# ffmpeg 자동 설치 (OS 감지 후 다운로드/설치) - 최초 실행 시 편리
python youtube_playlist_to_mp3.py "URL" --android --auto-install-ffmpeg
```

### 배치 파일 실행 (Windows - URL 입력만으로 간편)

```cmd
download_playlist.bat
```
실행 후 플레이리스트 URL을 입력하면 자동으로 다운로드됩니다. (Android 모드 기본 적용)

---

## ⚙️ 모든 옵션 상세

| 옵션 | 단축 | 기본값 | 설명 |
|------|------|--------|------|
| `url` | - | 필수 | YouTube 플레이리스트 URL |
| `--output-dir` | `-o` | `./downloads` 또는 플레이리스트 제목 | 출력 디렉토리 |
| `--quality` | `-q` | `0` | 오디오 품질 (0=최고 ~ 9=최저) |
| `--list-only` | | `False` | 다운로드하지 않고 목록만 출력 |
| `--no-thumbnail` | | `False` | 썸네일(앨범 아트) 임베드 안 함 |
| `--no-metadata` | | `False` | 메타데이터 태그 추가 안 함 |
| `--android` | | `False` | **Android 클라이언트 사용 (403 우회) - 권장** |
| `--cookies` | | `None` | 브라우저 쿠키 파일 경로 (Netscape 형식) |
| `--auto-install-ffmpeg` | | `False` | **ffmpeg 자동 설치 (OS 감지 후 다운로드/설치)** |
| `--use-playlist-title` | | `True` | 플레이리스트 제목으로 폴더 자동 생성 |
| `--no-playlist-title` | | `False` | 자동 폴더 생성 끄기 |

### 품질 설정 가이드 (`-q` / `--quality`)
| 값 | 비트레이트(대략) | 용도 |
|----|------------------|------|
| `0` | 320 kbps (최고) | 기본값, 고음질 보관용 |
| `2` | ~190 kbps | 일반적 사용 |
| `5` | ~130 kbps | 저장 공간 절약 |
| `9` | ~65 kbps (최저) | 최소 용량 |

---

## 📂 출력 예시

```
프로젝트/
├── youtube_playlist_to_mp3.py
├── download_playlist.bat
├── ffmpeg.exe              (직접 배치)
├── .gitignore
└── 플레이리스트제목/        (자동 생성)
    ├── 영상 제목 1.mp3
    ├── 영상 제목 2.mp3
    ├── 영상 제목 3.mp3
    └── ...
```

- 파일명: **영상 제목만** (번호 없음)
- 폴더명: **플레이리스트 제목** (자동 생성, 특수문자 `_`로 치환)
- 각 MP3에 썸네일 + 메타데이터 포함

---

## ❗ 문제 해결

### 403 Forbidden 에러
```bash
# --android 옵션 필수 추가
python youtube_playlist_to_mp3.py "URL" --android
```

### JavaScript 런타임 경고
```
WARNING: No supported JavaScript runtime could be found...
```
- `winget install deno` 설치 시 해결
- 경고만 뜨고 다운로드는 정상 진행됨

### 비공개/연령제한 영상
1. 브라우저에서 YouTube 로그인
2. [Get cookies.txt](https://chromewebstore.google.com/detail/get-cookiestxt-localy/cclelndahbckbenkjhflpdbgdldlbecc) 확장 프로그램으로 `cookies.txt` 내보내기
3. `--cookies cookies.txt` 옵션 추가

### ffmpeg를 찾을 수 없음
- 프로젝트 폴더에 `ffmpeg.exe` 배치
- 또는 시스템 PATH에 ffmpeg 경로 추가
- **`--auto-install-ffmpeg` 옵션으로 자동 설치** (Windows/Linux/macOS 지원)

---

## 📝 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 🙏 감사의 말

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 강력한 다운로드 엔진
- [ffmpeg](https://ffmpeg.org/) - 오디오/비디오 변환