#!/usr/bin/env python3
"""
Video Downloader GUI
漂亮的影片下載工具介面
"""

import re
import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    requests = None


class ModernStyle:
    """現代化深色主題樣式"""
    BG_DARK = "#1a1a2e"
    BG_CARD = "#16213e"
    BG_INPUT = "#0f3460"
    ACCENT = "#e94560"
    ACCENT_HOVER = "#ff6b6b"
    TEXT = "#eaeaea"
    TEXT_DIM = "#a0a0a0"
    SUCCESS = "#4ecca3"
    WARNING = "#ffc107"


class VideoDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader")
        self.root.geometry("600x500")
        self.root.configure(bg=ModernStyle.BG_DARK)
        self.root.resizable(False, False)

        # 設定樣式
        self.setup_styles()

        # 建立介面
        self.create_widgets()

        # 檢查依賴
        self.check_dependencies()

    def setup_styles(self):
        """設定 ttk 樣式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 設定按鈕樣式
        style.configure(
            "Accent.TButton",
            background=ModernStyle.ACCENT,
            foreground=ModernStyle.TEXT,
            padding=(20, 12),
            font=('Microsoft JhengHei UI', 11, 'bold')
        )
        style.map("Accent.TButton",
            background=[('active', ModernStyle.ACCENT_HOVER)]
        )

        style.configure(
            "Secondary.TButton",
            background=ModernStyle.BG_INPUT,
            foreground=ModernStyle.TEXT,
            padding=(12, 8),
            font=('Microsoft JhengHei UI', 9)
        )
        style.map("Secondary.TButton",
            background=[('active', ModernStyle.BG_CARD)]
        )

        # 進度條樣式
        style.configure(
            "Custom.Horizontal.TProgressbar",
            background=ModernStyle.ACCENT,
            troughcolor=ModernStyle.BG_INPUT,
            thickness=8
        )

    def create_widgets(self):
        """建立所有介面元件"""
        # 主容器
        main_frame = tk.Frame(self.root, bg=ModernStyle.BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # 標題
        title_label = tk.Label(
            main_frame,
            text="Video Downloader",
            font=('Microsoft JhengHei UI', 24, 'bold'),
            fg=ModernStyle.TEXT,
            bg=ModernStyle.BG_DARK
        )
        title_label.pack(pady=(0, 5))

        subtitle_label = tk.Label(
            main_frame,
            text="支援 m3u8 串流影片下載",
            font=('Microsoft JhengHei UI', 10),
            fg=ModernStyle.TEXT_DIM,
            bg=ModernStyle.BG_DARK
        )
        subtitle_label.pack(pady=(0, 25))

        # URL 輸入區
        url_frame = tk.Frame(main_frame, bg=ModernStyle.BG_CARD)
        url_frame.pack(fill=tk.X, pady=(0, 15))
        url_frame.pack_propagate(False)
        url_frame.configure(height=90)

        url_inner = tk.Frame(url_frame, bg=ModernStyle.BG_CARD)
        url_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        url_label = tk.Label(
            url_inner,
            text="影片網址",
            font=('Microsoft JhengHei UI', 10, 'bold'),
            fg=ModernStyle.TEXT,
            bg=ModernStyle.BG_CARD
        )
        url_label.pack(anchor=tk.W)

        self.url_entry = tk.Entry(
            url_inner,
            font=('Consolas', 11),
            bg=ModernStyle.BG_INPUT,
            fg=ModernStyle.TEXT,
            insertbackground=ModernStyle.TEXT,
            relief=tk.FLAT,
            highlightthickness=2,
            highlightbackground=ModernStyle.BG_INPUT,
            highlightcolor=ModernStyle.ACCENT
        )
        self.url_entry.pack(fill=tk.X, pady=(8, 0), ipady=8)

        # 輸出設定區
        output_frame = tk.Frame(main_frame, bg=ModernStyle.BG_CARD)
        output_frame.pack(fill=tk.X, pady=(0, 15))
        output_frame.pack_propagate(False)
        output_frame.configure(height=90)

        output_inner = tk.Frame(output_frame, bg=ModernStyle.BG_CARD)
        output_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        output_label = tk.Label(
            output_inner,
            text="輸出檔案",
            font=('Microsoft JhengHei UI', 10, 'bold'),
            fg=ModernStyle.TEXT,
            bg=ModernStyle.BG_CARD
        )
        output_label.pack(anchor=tk.W)

        output_row = tk.Frame(output_inner, bg=ModernStyle.BG_CARD)
        output_row.pack(fill=tk.X, pady=(8, 0))

        self.output_entry = tk.Entry(
            output_row,
            font=('Consolas', 11),
            bg=ModernStyle.BG_INPUT,
            fg=ModernStyle.TEXT,
            insertbackground=ModernStyle.TEXT,
            relief=tk.FLAT,
            highlightthickness=2,
            highlightbackground=ModernStyle.BG_INPUT,
            highlightcolor=ModernStyle.ACCENT
        )
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.output_entry.insert(0, "video.mp4")

        browse_btn = ttk.Button(
            output_row,
            text="瀏覽...",
            style="Secondary.TButton",
            command=self.browse_output
        )
        browse_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # 工具選擇
        tool_frame = tk.Frame(main_frame, bg=ModernStyle.BG_DARK)
        tool_frame.pack(fill=tk.X, pady=(0, 20))

        tool_label = tk.Label(
            tool_frame,
            text="下載工具：",
            font=('Microsoft JhengHei UI', 10),
            fg=ModernStyle.TEXT_DIM,
            bg=ModernStyle.BG_DARK
        )
        tool_label.pack(side=tk.LEFT)

        self.tool_var = tk.StringVar(value="auto")

        for text, value in [("自動選擇", "auto"), ("yt-dlp", "yt-dlp"), ("ffmpeg", "ffmpeg")]:
            rb = tk.Radiobutton(
                tool_frame,
                text=text,
                variable=self.tool_var,
                value=value,
                font=('Microsoft JhengHei UI', 10),
                fg=ModernStyle.TEXT,
                bg=ModernStyle.BG_DARK,
                selectcolor=ModernStyle.BG_INPUT,
                activebackground=ModernStyle.BG_DARK,
                activeforeground=ModernStyle.TEXT
            )
            rb.pack(side=tk.LEFT, padx=(15, 0))

        # 狀態顯示區
        self.status_frame = tk.Frame(main_frame, bg=ModernStyle.BG_CARD)
        self.status_frame.pack(fill=tk.X, pady=(0, 20))
        self.status_frame.pack_propagate(False)
        self.status_frame.configure(height=80)

        status_inner = tk.Frame(self.status_frame, bg=ModernStyle.BG_CARD)
        status_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        self.status_label = tk.Label(
            status_inner,
            text="準備就緒",
            font=('Microsoft JhengHei UI', 10),
            fg=ModernStyle.TEXT_DIM,
            bg=ModernStyle.BG_CARD
        )
        self.status_label.pack(anchor=tk.W)

        self.progress = ttk.Progressbar(
            status_inner,
            style="Custom.Horizontal.TProgressbar",
            mode='indeterminate'
        )
        self.progress.pack(fill=tk.X, pady=(10, 0))

        # 工具狀態
        self.tools_label = tk.Label(
            status_inner,
            text="",
            font=('Microsoft JhengHei UI', 9),
            fg=ModernStyle.TEXT_DIM,
            bg=ModernStyle.BG_CARD
        )
        self.tools_label.pack(anchor=tk.W, pady=(8, 0))

        # 下載按鈕
        self.download_btn = ttk.Button(
            main_frame,
            text="開始下載",
            style="Accent.TButton",
            command=self.start_download
        )
        self.download_btn.pack(pady=(0, 10))

        # 版權資訊
        footer = tk.Label(
            main_frame,
            text="支援 gimy.com.tw 等網站的 m3u8 串流",
            font=('Microsoft JhengHei UI', 9),
            fg=ModernStyle.TEXT_DIM,
            bg=ModernStyle.BG_DARK
        )
        footer.pack(side=tk.BOTTOM)

    def browse_output(self):
        """選擇輸出檔案位置"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 影片", "*.mp4"), ("所有檔案", "*.*")],
            initialfile=self.output_entry.get() or "video.mp4"
        )
        if filename:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filename)

    def check_dependencies(self):
        """檢查必要的下載工具"""
        tools = {}

        # 檢查 yt-dlp
        try:
            result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
            tools['yt-dlp'] = result.returncode == 0
        except FileNotFoundError:
            tools['yt-dlp'] = False

        # 檢查 ffmpeg
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            tools['ffmpeg'] = result.returncode == 0
        except FileNotFoundError:
            tools['ffmpeg'] = False

        self.available_tools = tools

        # 更新狀態
        status_parts = []
        for name, available in tools.items():
            icon = "✓" if available else "✗"
            status_parts.append(f"{name}: {icon}")
        self.tools_label.config(text="  |  ".join(status_parts))

        if not any(tools.values()):
            self.status_label.config(
                text="⚠ 需要安裝 yt-dlp 或 ffmpeg",
                fg=ModernStyle.WARNING
            )

    def extract_m3u8_url(self, page_url):
        """從網頁中提取 m3u8 影片網址"""
        if not requests:
            return None

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': page_url,
        }

        try:
            response = requests.get(page_url, headers=headers, timeout=30)
            response.raise_for_status()
            html = response.text

            patterns = [
                r'"url"\s*:\s*"([^"]+\.m3u8[^"]*)"',
                r"'url'\s*:\s*'([^']+\.m3u8[^']*)'",
                r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, html)
                if matches:
                    url = matches[0]
                    url = url.replace('\\/', '/')
                    return url

            return None

        except Exception as e:
            self.update_status(f"解析錯誤: {e}", ModernStyle.ACCENT)
            return None

    def update_status(self, message, color=None):
        """更新狀態訊息"""
        self.status_label.config(
            text=message,
            fg=color or ModernStyle.TEXT_DIM
        )
        self.root.update()

    def start_download(self):
        """開始下載"""
        url = self.url_entry.get().strip()
        output = self.output_entry.get().strip()

        if not url:
            messagebox.showwarning("提示", "請輸入影片網址")
            return

        if not output:
            messagebox.showwarning("提示", "請設定輸出檔案")
            return

        if not any(self.available_tools.values()):
            messagebox.showerror("錯誤", "需要安裝 yt-dlp 或 ffmpeg\n\n安裝 yt-dlp: pip install yt-dlp")
            return

        # 禁用按鈕
        self.download_btn.config(state=tk.DISABLED)
        self.progress.start(10)

        # 在背景執行下載
        thread = threading.Thread(target=self.download_thread, args=(url, output))
        thread.daemon = True
        thread.start()

    def download_thread(self, url, output):
        """下載執行緒"""
        try:
            # 判斷是直接的 m3u8 還是網頁
            m3u8_url = url
            page_url = url

            if '.m3u8' not in url.lower():
                self.update_status("正在解析網頁...")
                m3u8_url = self.extract_m3u8_url(url)

                if not m3u8_url:
                    self.update_status("無法從網頁中提取影片網址", ModernStyle.ACCENT)
                    self.finish_download(False)
                    return

            self.update_status(f"找到影片: {m3u8_url[:50]}...")

            # 選擇工具
            tool = self.tool_var.get()
            if tool == "auto":
                tool = "yt-dlp" if self.available_tools.get('yt-dlp') else "ffmpeg"

            self.update_status(f"正在使用 {tool} 下載...")

            # 執行下載
            referer = page_url

            if tool == "yt-dlp":
                cmd = [
                    'yt-dlp', '-o', output,
                    '--referer', referer,
                    '--no-check-certificates',
                    '-f', 'best',
                    m3u8_url
                ]
            else:
                cmd = [
                    'ffmpeg', '-y',
                    '-headers', f'Referer: {referer}',
                    '-i', m3u8_url,
                    '-c', 'copy',
                    '-bsf:a', 'aac_adtstoasc',
                    output
                ]

            process = subprocess.run(cmd, capture_output=True, text=True)

            if process.returncode == 0:
                # 檢查檔案大小
                if os.path.exists(output):
                    size_mb = os.path.getsize(output) / (1024 * 1024)
                    self.update_status(f"✓ 下載完成！({size_mb:.1f} MB)", ModernStyle.SUCCESS)
                else:
                    self.update_status("✓ 下載完成！", ModernStyle.SUCCESS)
                self.finish_download(True)
            else:
                self.update_status("✗ 下載失敗", ModernStyle.ACCENT)
                self.finish_download(False)

        except Exception as e:
            self.update_status(f"錯誤: {e}", ModernStyle.ACCENT)
            self.finish_download(False)

    def finish_download(self, success):
        """下載完成"""
        self.progress.stop()
        self.download_btn.config(state=tk.NORMAL)

        if success:
            self.root.after(0, lambda: messagebox.showinfo("完成", "影片下載完成！"))


def main():
    root = tk.Tk()

    # 設定視窗圖示（如果有的話）
    try:
        root.iconbitmap('icon.ico')
    except:
        pass

    app = VideoDownloaderGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
