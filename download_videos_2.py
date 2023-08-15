import tkinter as tk
from tkinter import filedialog
import yt_dlp
import threading

def clean_name(name):
    return ''.join(e for e in name if e.isalnum() or e in ' ._')

def hook(d):
    if d['status'] == 'downloading':
        downloaded_bytes = d['downloaded_bytes']
        total_bytes = d.get('total_bytes') or 1  # Guard against division by zero
        speed = d.get('speed', None)
        eta = d.get('eta', None)
        
        if speed is not None:
            speed_str = f'{speed / 1_000_000:.2f}MiB/s'
        else:
            speed_str = '---'
        
        if eta is not None:
            eta_str = f'ETA {eta // 60:02}:{eta % 60:02}'
        else:
            eta_str = '---:--'
        
        progress.set(f'{downloaded_bytes / total_bytes * 100:.1f}% of {total_bytes / 1_000_000:.2f}MiB at {speed_str} {eta_str}')

def fetch_info():
    url = url_entry.get()
    with yt_dlp.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(url, download=False)
        title.set(clean_name(info_dict['title']))
        next_step()

def next_step():
    url_label.pack_forget()
    url_entry.pack_forget()
    path_label.pack_forget()
    path_button.pack_forget()
    next_button.pack_forget()
    
    title_label.pack()
    title_entry.pack()
    confirm_button.pack()

def browse_folder():
    folder_selected = filedialog.askdirectory()
    path_var.set(folder_selected)

def download_video():
    def threaded_download():
        url = url_entry.get()
        path = path_var.get()
        final_title = title.get()

        ydl_opts = {
            'outtmpl': f'{path}/{final_title}.%(ext)s',
            'progress_hooks': [hook],
        }

        title_label['text'] = f"Downloading '{final_title}'"
        title_entry.pack_forget()
        confirm_button.pack_forget()

        progress_label.pack()
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        root.quit()

    threading.Thread(target=threaded_download).start()

root = tk.Tk()
root.title("YouTube Downloader")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Setting window size to 40% of screen size
root.geometry(f"{int(screen_width * 0.2)}x{int(screen_height * 0.2)}")

url_label = tk.Label(root, text="YouTube URL:")
url_label.pack(pady=10)

url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=10)

path_label = tk.Label(root, text="Save to:")
path_label.pack(pady=10)

path_var = tk.StringVar()
path_button = tk.Button(root, text="Browse", command=browse_folder)
path_button.pack(pady=10)

next_button = tk.Button(root, text="Next", command=fetch_info)
next_button.pack(pady=10)

title = tk.StringVar(root)
title_label = tk.Label(root, text="Video Title:")
title_entry = tk.Entry(root, textvariable=title, width=50)

confirm_button = tk.Button(root, text="Confirm & Download", command=download_video)

progress = tk.StringVar(root, value="Waiting for download...")
progress_label = tk.Label(root, textvariable=progress)

root.mainloop()
