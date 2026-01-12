#!/usr/bin/env python3
"""
Video Downloader Tool
支援從 gimy.com.tw 等網站下載 m3u8 串流影片
"""

import re
import os
import sys
import subprocess
import argparse
from urllib.parse import urlparse, unquote

try:
    import requests
except ImportError:
    print("請先安裝 requests: pip install requests")
    sys.exit(1)


def extract_m3u8_url(page_url: str) -> str | None:
    """從網頁中提取 m3u8 影片網址"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': page_url,
    }

    try:
        response = requests.get(page_url, headers=headers, timeout=30)
        response.raise_for_status()
        html = response.text

        # 嘗試多種模式來提取 m3u8 網址
        patterns = [
            r'"url"\s*:\s*"([^"]+\.m3u8[^"]*)"',  # JSON 格式
            r"'url'\s*:\s*'([^']+\.m3u8[^']*)'",  # 單引號 JSON
            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',  # 直接 URL
            r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',  # source 屬性
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html)
            if matches:
                url = matches[0] if isinstance(matches[0], str) else matches[0]
                # 處理轉義字元
                url = url.replace('\\/', '/')
                return url

        return None

    except requests.RequestException as e:
        print(f"網頁請求錯誤: {e}")
        return None


def check_dependencies() -> dict:
    """檢查必要的下載工具"""
    tools = {}

    # 檢查 yt-dlp
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            tools['yt-dlp'] = True
    except FileNotFoundError:
        tools['yt-dlp'] = False

    # 檢查 ffmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            tools['ffmpeg'] = True
    except FileNotFoundError:
        tools['ffmpeg'] = False

    return tools


def download_with_ytdlp(url: str, output: str, referer: str = None) -> bool:
    """使用 yt-dlp 下載影片"""
    cmd = ['yt-dlp', '-o', output]

    if referer:
        cmd.extend(['--referer', referer])

    cmd.extend([
        '--no-check-certificates',
        '-f', 'best',
        url
    ])

    print(f"執行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode == 0


def download_with_ffmpeg(url: str, output: str, referer: str = None) -> bool:
    """使用 ffmpeg 下載影片"""
    cmd = ['ffmpeg', '-y']

    if referer:
        cmd.extend(['-headers', f'Referer: {referer}'])

    cmd.extend([
        '-i', url,
        '-c', 'copy',  # 直接複製，不重新編碼
        '-bsf:a', 'aac_adtstoasc',
        output
    ])

    print(f"執行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode == 0


def generate_output_filename(page_url: str, m3u8_url: str) -> str:
    """根據網址生成輸出檔名"""
    # 嘗試從網頁 URL 提取資訊
    parsed = urlparse(page_url)
    path_parts = parsed.path.strip('/').replace('.html', '').split('/')

    if path_parts:
        name = path_parts[-1]
        # 清理檔名
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        return f"{name}.mp4"

    return "video.mp4"


def main():
    parser = argparse.ArgumentParser(
        description='影片下載工具 - 支援 m3u8 串流下載',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用範例:
  python video_downloader.py https://gimy.com.tw/video/58422-11.html
  python video_downloader.py https://gimy.com.tw/video/58422-11.html -o 星廚之戰_EP11.mp4
  python video_downloader.py --m3u8 https://v.lzcdn28.com/xxx/index.m3u8 -o video.mp4

安裝依賴:
  pip install requests

  # 安裝 yt-dlp (推薦)
  pip install yt-dlp

  # 或安裝 ffmpeg
  # Windows: winget install ffmpeg
  # 或從 https://ffmpeg.org/download.html 下載
        '''
    )

    parser.add_argument('url', nargs='?', help='影片網頁網址')
    parser.add_argument('--m3u8', '-m', help='直接指定 m3u8 網址')
    parser.add_argument('--output', '-o', help='輸出檔案名稱')
    parser.add_argument('--tool', '-t', choices=['yt-dlp', 'ffmpeg'], help='指定下載工具')

    args = parser.parse_args()

    if not args.url and not args.m3u8:
        parser.print_help()
        sys.exit(1)

    # 檢查依賴
    tools = check_dependencies()
    print(f"可用工具: yt-dlp={'[OK]' if tools.get('yt-dlp') else '[X]'}, ffmpeg={'[OK]' if tools.get('ffmpeg') else '[X]'}")

    if not any(tools.values()):
        print("\n錯誤: 需要安裝 yt-dlp 或 ffmpeg")
        print("安裝 yt-dlp: pip install yt-dlp")
        print("安裝 ffmpeg: winget install ffmpeg")
        sys.exit(1)

    # 取得 m3u8 網址
    m3u8_url = args.m3u8
    page_url = args.url

    if not m3u8_url and page_url:
        print(f"正在解析網頁: {page_url}")
        m3u8_url = extract_m3u8_url(page_url)

        if not m3u8_url:
            print("錯誤: 無法從網頁中提取影片網址")
            sys.exit(1)

    print(f"影片網址: {m3u8_url}")

    # 設定輸出檔名
    output = args.output or generate_output_filename(page_url or '', m3u8_url)
    print(f"輸出檔案: {output}")

    # 選擇下載工具
    if args.tool:
        tool = args.tool
    elif tools.get('yt-dlp'):
        tool = 'yt-dlp'
    else:
        tool = 'ffmpeg'

    print(f"使用工具: {tool}")
    print("-" * 50)

    # 執行下載
    referer = page_url or urlparse(m3u8_url).scheme + '://' + urlparse(m3u8_url).netloc

    if tool == 'yt-dlp':
        success = download_with_ytdlp(m3u8_url, output, referer)
    else:
        success = download_with_ffmpeg(m3u8_url, output, referer)

    if success:
        print("-" * 50)
        print(f"下載完成: {output}")
        if os.path.exists(output):
            size_mb = os.path.getsize(output) / (1024 * 1024)
            print(f"檔案大小: {size_mb:.2f} MB")
    else:
        print("下載失敗")
        sys.exit(1)


if __name__ == '__main__':
    main()
