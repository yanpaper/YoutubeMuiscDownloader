# YouTube Playlist to MP3 Downloader

A tool to download all videos from a YouTube playlist as MP3 files.

## ✨ Features

- 🎵 **Full Playlist Download** - Convert entire playlists to MP3 in order
- 🖼️ **Thumbnail Embedding** - Album art automatically embedded
- 🏷️ **Metadata Tags** - Title, artist, album, and other tags auto-populated
- 📁 **Auto Folder Creation** - Creates folder named after playlist title
- 🔄 **403 Forbidden Bypass** - Android client mode support
- 🍪 **Cookie Support** - Download private/age-restricted videos
- ⚡ **Local ffmpeg Auto-Detection** - No separate install needed (just place ffmpeg.exe in folder)

---

## 📋 Prerequisites

| Program | Installation |
|---------|--------------|
| **Python** | 3.8+ recommended |
| **yt-dlp** | `pip install yt-dlp` |
| **ffmpeg** | Place `ffmpeg.exe` in project folder OR add to PATH via [official site](https://ffmpeg.org/download.html) |

> **Note:** This repository does not include `ffmpeg.exe` (excluded by `.gitignore`). Download and place it in the project root.

---

## 🚀 Installation & Usage

### 1. Clone Repository
```bash
git clone https://github.com/yanpaper/YoutubeMuiscDownloader.git
cd YoutubeMuiscDownloader
```

### 2. Install Dependencies
```bash
pip install yt-dlp
```

### 3. Place ffmpeg (Optional - auto-detected if in project folder)
- Download `ffmpeg-essentials_build.zip` from [official builds](https://www.gyan.dev/ffmpeg/builds/)
- Extract and copy `ffmpeg.exe` to project root

---

## 💻 Usage

### Python Direct Execution (Recommended - Full Options)

```bash
# Basic: Auto folder by playlist title + Android mode (403 bypass)
python youtube_playlist_to_mp3.py "https://www.youtube.com/playlist?list=PLxxx" --android

# Custom output directory
python youtube_playlist_to_mp3.py "URL" -o ./my_music --android

# High quality (0=best, 9=worst, default 0)
python youtube_playlist_to_mp3.py "URL" -q 0 --android

# Preview only (no download, ffmpeg not needed)
python youtube_playlist_to_mp3.py "URL" --list-only

# Skip thumbnail embedding
python youtube_playlist_to_mp3.py "URL" --no-thumbnail --android

# Skip metadata tags
python youtube_playlist_to_mp3.py "URL" --no-metadata --android

# Private/age-restricted videos - browser cookies
python youtube_playlist_to_mp3.py "URL" --cookies cookies.txt --android

# Disable auto playlist-title folder (use default downloads folder)
python youtube_playlist_to_mp3.py "URL" --no-playlist-title --android
```

### Batch File (Windows - Simple URL Input)

```cmd
download_playlist.bat
```
Run and enter playlist URL when prompted. (Android mode enabled by default)

---

## ⚙️ All Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `url` | - | Required | YouTube playlist URL |
| `--output-dir` | `-o` | `./downloads` or playlist title | Output directory |
| `--quality` | `-q` | `0` | Audio quality (0=best ~ 9=worst) |
| `--list-only` | | `False` | List playlist only, no download |
| `--no-thumbnail` | | `False` | Skip thumbnail/album art embedding |
| `--no-metadata` | | `False` | Skip metadata tag writing |
| `--android` | | `False` | **Use Android client (bypass 403) - Recommended** |
| `--cookies` | | `None` | Browser cookies file path (Netscape format) |
| `--use-playlist-title` | | `True` | Auto-create folder from playlist title |
| `--no-playlist-title` | | `False` | Disable auto folder creation |

### Quality Guide (`-q` / `--quality`)

| Value | Approx. Bitrate | Use Case |
|-------|-----------------|----------|
| `0` | 320 kbps (Best) | Default, archival quality |
| `2` | ~190 kbps | General listening |
| `5` | ~130 kbps | Save storage space |
| `9` | ~65 kbps (Worst) | Minimum size |

---

## 📂 Output Structure

```
project/
├── youtube_playlist_to_mp3.py
├── download_playlist.bat
├── ffmpeg.exe              (place manually)
├── .gitignore
└── PlaylistTitle/          (auto-created)
    ├── Video Title 1.mp3
    ├── Video Title 2.mp3
    ├── Video Title 3.mp3
    └── ...
```

- **Filename**: Video title only (no track numbers)
- **Folder**: Playlist title (auto-generated, invalid chars replaced with `_`)
- **Each MP3**: Contains embedded thumbnail + metadata

---

## ❗ Troubleshooting

### 403 Forbidden Error
```bash
# Add --android option (required)
python youtube_playlist_to_mp3.py "URL" --android
```

### JavaScript Runtime Warning
```
WARNING: No supported JavaScript runtime could be found...
```
- Fix: `winget install deno`
- Warning only, download proceeds normally

### Private/Age-Restricted Videos
1. Log into YouTube in browser
2. Export cookies using [Get cookies.txt](https://chromewebstore.google.com/detail/get-cookiestxt-localy/cclelndahbckbenkjhflpdbgdldlbecc) extension
3. Add `--cookies cookies.txt` option

### ffmpeg Not Found
- Place `ffmpeg.exe` in project folder
- Or add ffmpeg to system PATH

---

## 📝 License

MIT License - Free to use, modify, and distribute

---

## 🙏 Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Powerful download engine
- [ffmpeg](https://ffmpeg.org/) - Audio/video conversion