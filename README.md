# Video Downloader

影片下載工具 - 支援 m3u8 串流影片下載

## 功能

- 從影片網頁自動提取 m3u8 網址
- 支援 yt-dlp 和 ffmpeg 兩種下載方式
- 支援自訂輸出檔名
- **GUI 圖形介面** - 簡單易用的視覺化操作

## 下載

從 [Releases](../../releases) 下載：

| 檔案 | 說明 |
|------|------|
| `video_downloader_gui.exe` | **推薦** - 圖形介面版本 |
| `video_downloader.exe` | 命令列版本 |

## 截圖

GUI 版本提供現代化深色主題介面，操作簡單直覺。

## 使用方式

### GUI 版本

1. 執行 `video_downloader_gui.exe`
2. 貼上影片網址
3. 選擇輸出位置
4. 點擊「開始下載」

### 命令列版本

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

## 開發

```bash
# 安裝依賴
pip install requests pyinstaller

# 執行 GUI 版本
python video_downloader_gui.py

# 執行命令列版本
python video_downloader.py

# 打包
pyinstaller --onefile --noconsole --name video_downloader_gui video_downloader_gui.py
pyinstaller --onefile --name video_downloader video_downloader.py
```
