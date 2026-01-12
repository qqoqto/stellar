# Video Downloader

影片下載工具 - 支援 m3u8 串流影片下載

## 功能

- 從影片網頁自動提取 m3u8 網址
- 支援 yt-dlp 和 ffmpeg 兩種下載方式
- 支援自訂輸出檔名

## 下載

從 [Releases](../../releases) 下載 `video_downloader.exe`

## 使用方式

```bash
# 從網頁下載
video_downloader.exe https://example.com/video.html

# 指定輸出檔名
video_downloader.exe https://example.com/video.html -o output.mp4

# 直接指定 m3u8 網址
video_downloader.exe --m3u8 https://example.com/video.m3u8 -o output.mp4
```

## 依賴

需要安裝以下其中一個工具：
- [yt-dlp](https://github.com/yt-dlp/yt-dlp): `pip install yt-dlp`
- [ffmpeg](https://ffmpeg.org/download.html): `winget install ffmpeg`
