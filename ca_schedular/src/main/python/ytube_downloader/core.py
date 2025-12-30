
# ytube_downloader/core.py


import yt_dlp
import os

# ───────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ───────────────────────────────────────────────────────────────────────────────


YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=q6EoRBvdVPQ",
    "https://www.youtube.com/watch?v=FSXsAt7z_RU",
    "https://www.youtube.com/watch?v=9fCNNuH-Grg",
    "https://www.youtube.com/watch?v=45A_9y1ClAQ",
    "https://www.youtube.com/watch?v=nz2_gNQDiVM",
    "https://www.youtube.com/watch?v=1wYNFfgrXTI",
    # "https://www.youtube.com/watch?v=FSXsAt7z_RU",
    # Add more URLs here
]


OUTPUT_DIR  = "./downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ───────────────────────────────────────────────────────────────────────────────
# DOWNLOAD BEST PROGRESSIVE MP4 (video+audio already in one file)
# ───────────────────────────────────────────────────────────────────────────────
def download_progressive_mp4(youtube_url: str, output_dir: str):
    """
    Tells yt-dlp to fetch the best progressive MP4 (which has audio+video together).
    That way, no merging is required, and ffmpeg is not invoked.
    """
    # ydl_opts = {
    #     # "best[ext=mp4]" picks the best single‐file MP4 (with audio+video embedded).
    #     # If no MP4 progressive is available, it will fallback to "best" of any container.
    #     "format": "best[ext=mp4]/best",
    #     "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
    #     "noplaylist": True,
    #     "quiet": False,     # set to True if you want less output
    #     "no_warnings": True
    # }


    """
    Tells yt-dlp to fetch the best progressive MP4 (which has audio+video together).
    That way, no merging is required, and ffmpeg is not invoked.
    Tries to get the highest resolution progressive MP4 available.
    """
    ydl_opts = {
        # "bestvideo[ext=mp4][vcodec^=avc1][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        # will try to get the best progressive MP4 up to 1080p, else fallback.
        "format": "bestvideo[ext=mp4][vcodec^=avc1][height<=2160]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": False,     # set to True if you want less output
        "no_warnings": True
    }


    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        filename = ydl.prepare_filename(info_dict)
        return filename


# ───────────────────────────────────────────────────────────────────────────────
# DOWNLOAD BEST AUDIO‐ONLY (without converting to MP3; this will be M4A or WebM)
# ───────────────────────────────────────────────────────────────────────────────
def download_best_audio_without_conversion(youtube_url: str, output_dir: str):
    """
    Downloads the best audio‐only stream (often .m4a or .webm), without running
    a postprocessor (i.e., no conversion to MP3). This way, we avoid needing ffmpeg.
    """
    ydl_opts = {
        # "bestaudio[ext=m4a]/bestaudio" picks best M4A if available, else best audio of any type.
        "format": "bestaudio[ext=m4a]/bestaudio",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": False,
        "no_warnings": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        filename = ydl.prepare_filename(info_dict)
        return filename

def download_best_mp3_with_ffmpeg(youtube_url: str, output_dir: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "noplaylist": True,
        "quiet": False,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        # final filename will be something like "Some Title.mp3"
        base, _ = os.path.splitext(ydl.prepare_filename(info))
        return base + ".mp3"





def main():
    for url in YOUTUBE_URLS:
        print(f"Downloading best progressive MP4 (no merging) for {url}…")
        mp4_path = download_progressive_mp4(url, OUTPUT_DIR)
        print(f"  → Saved MP4 Progressively to: {mp4_path}")

        print(f"Downloading best audio‐only (no MP3 conversion) for {url}…")
        audio_path = download_best_audio_without_conversion(url, OUTPUT_DIR)
        audio_path = download_best_mp3_with_ffmpeg(url, OUTPUT_DIR)
        print(f"  → Saved audio stream to: {audio_path}")

    print("\nDone. (If you need an actual .mp3, you must install ffmpeg and re-run with a postprocessor.)")
