import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pytube import YouTube
import yt_dlp
import threading
import os

class VideoDownloader:
    def __init__(self, master):
        self.master = master
        master.title("Video downloader")

        self.url_label = ttk.Label(master, text="Video link:")
        self.url_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.url_entry = ttk.Entry(master, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.download_path_label = ttk.Label(master, text="Path:")
        self.download_path_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.download_path_entry = ttk.Entry(master, width=40)
        self.download_path_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.download_path_entry.insert(0, os.path.expanduser("~"))

        self.browse_button = ttk.Button(master, text="View...", command=self.browse_directory)
        self.browse_button.grid(row=1, column=2, padx=5, pady=5)

        self.download_button = ttk.Button(master, text="Download", command=self.start_download)
        self.download_button.grid(row=2, column=0, columnspan=3, padx=5, pady=10)

        self.status_label = ttk.Label(master, text="")
        self.status_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        master.grid_columnconfigure(1, weight=1)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_path_entry.delete(0, tk.END)
            self.download_path_entry.insert(0, directory)

    def start_download(self):
        url = self.url_entry.get()
        download_path = self.download_path_entry.get()

        if not url:
            messagebox.showerror("Error", "Please, insert video link.")
            return

        if not download_path:
            messagebox.showerror("Error", "Please, choose downloading path.")
            return

        threading.Thread(target=self.download_video, args=(url, download_path)).start()
        self.status_label.config(text="Downloading...")

    def download_video(self, url, download_path):
        try:
            if "youtube.com" in url:
                self.download_youtube(url, download_path)
            elif "tiktok.com" in url or "instagram.com" in url:
                self.download_with_yt_dlp(url, download_path)
            else:
                self.status_label.config(text="Link not recognized.")
                messagebox.showerror("Error", "Link not recognized. Supports only YouTube, TikTok and Instagram.")
        except Exception as e:
            self.status_label.config(text=f"Downloading error: {e}")
            messagebox.showerror("Downloading error", str(e))

    def download_youtube(self, url, download_path):
        try:
            yt = YouTube(url, on_progress_callback=self.show_progress)
            streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
            best_stream = streams.first()

            self.status_label.config(text=f"Downloading: {yt.title}")
            best_stream.download(output_path=download_path)
            self.status_label.config(text=f"Download complete: {yt.title}")
            messagebox.showinfo("Success", f"video '{yt.title}' successfully downloaded!")
        except Exception as e:
            self.status_label.config(text=f"Error downloading from YouTube: {e}")
            messagebox.showerror("Error downloading from YouTube", str(e))

    def download_with_yt_dlp(self, url, download_path):
        try:
            ydl_opts = {
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.yt_dlp_progress_hook],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_title = info_dict.get('title', 'Unknown')
                self.status_label.config(text=f"Download complete: {video_title}")
                messagebox.showinfo("Success", f"Video '{video_title}' successfully downloaded!")
        except Exception as e:
            self.status_label.config(text=f"Download error: {e}")
            messagebox.showerror("Download error", str(e))

    def show_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        self.status_label.config(text=f"Downloading: {percentage:.2f}%")

    def yt_dlp_progress_hook(self, d):
        if d['status'] == 'downloading':
            percentage = d['_percent_str']
            self.master.after(0, self.status_label.config, {"text": f"Downloading: {percentage}"})
        elif d['status'] == 'finished':
            self.master.after(0, self.status_label.config, {"text": "Processing complete..."})

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloader(root)
    root.mainloop()