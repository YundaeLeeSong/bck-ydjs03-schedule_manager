# Using yt-dlp and Managing ffmpeg Dependencies

The error you’re seeing:

```
ERROR: You have requested merging of multiple formats but ffmpeg is not installed. Aborting due to --abort-on-error
```

happens because by default we told **yt-dlp** to download a separate “video‐only” MP4 stream plus an “audio‐only” M4A stream and then merge them. Merging requires **ffmpeg** (or an equivalent muxer) on your system’s PATH. You have two main ways to fix this:

1. **Install ffmpeg** so that yt-dlp can merge adaptive streams into a single MP4/MP3.  
2. **Change your format string** so that yt-dlp only grabs a single “progressive” MP4 (video+audio in one file) and/or skips MP3 conversion, thus avoiding any merging step.

Below are both approaches in detail.

---

## 1. Installing ffmpeg (Recommended)

If you want yt-dlp to continue merging adaptive video+audio (and to convert audio to MP3 automatically), you simply need to install **ffmpeg** on your machine and make sure it’s on your PATH.

### 1.1 Download and Install ffmpeg on Windows

1. Go to the official FFmpeg download page for Windows:  
   https://www.gyan.dev/ffmpeg/builds/  
   (You can also use https://www.ffmpeg.org/download.html → Windows builds.)

2. Under “Release Builds,” click the link for “git full” (or “git essentials”) to download a ZIP. For example:  
   ```
   https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
   ```

3. Unzip the downloaded folder (e.g. you’ll get a folder named `ffmpeg-<version>-essentials_win64`).

4. Inside that unzipped folder, you’ll find a `bin/` directory containing `ffmpeg.exe`.  
   Copy the **entire “bin” folder** (that contains `ffmpeg.exe`, `ffprobe.exe`, etc.) to a location of your choice, for example:  
   ```
   C:\ffmpeg\bin\
   ```

5. Add `C:\ffmpeg\bin\` to your Windows PATH:

   - Press Win + R, type `sysdm.cpl`, and press Enter.  
   - Go to the “Advanced” tab → click “Environment Variables…”.  
   - Under “System variables,” find and select `Path`, then click “Edit…”.  
   - Click “New” and type:
     ```
     C:\ffmpeg\bin
     ```
   - Click “OK” on all dialogs to save.

6. Open a **new** Command Prompt (so that the updated PATH is loaded), and type:
   ```cmd
   ffmpeg -version
   ```
   You should see ffmpeg’s version info. If you see that, yt-dlp will now be able to invoke ffmpeg automatically.

7. Re-run your Python script that uses yt-dlp. The merge step (video + audio to MP4, and audio→MP3 conversion) will now succeed.

---

## 2. Using Only Progressive (Video+Audio in One File) and Skipping MP3 Conversion

If you cannot install ffmpeg or prefer not to depend on it, you can modify your **yt-dlp** options so that:

- You only download a single progressive MP4 (which already contains both audio + video). No merging needed.  
- You do _not_ run the FFmpegExtractAudio post‐processor (so you end up with, say, a WebM or M4A file instead of an MP3). If you truly need “.mp3,” then you must have ffmpeg. But you can still grab the highest‐bitrate audio container (often WebM/Opus or M4A) without ffmpeg.

Below is a revised script that:

1. Downloads the best progressive MP4 (video+audio bundled in one file).  
2. Downloads the best audio‐only stream as “.m4a” (no ffmpeg required).  
   - If you really need MP3, you must install ffmpeg. This example will show you how to grab M4A or WebM audio without conversion.

```python
import yt_dlp
import os

# ───────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ───────────────────────────────────────────────────────────────────────────────

YOUTUBE_URL = "https://www.youtube.com/watch?v=0PmvcOSPI6A"
OUTPUT_DIR  = "./downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ───────────────────────────────────────────────────────────────────────────────
# DOWNLOAD BEST PROGRESSIVE MP4 (video+audio already in one file)
# ───────────────────────────────────────────────────────────────────────────────
def download_progressive_mp4(youtube_url: str, output_dir: str):
    '''
    Tells yt-dlp to fetch the best progressive MP4 (which has audio+video together).
    That way, no merging is required, and ffmpeg is not invoked.
    '''
    ydl_opts = {
        # "best[ext=mp4]" picks the best single‐file MP4 (with audio+video embedded).
        # If no MP4 progressive is available, it will fallback to "best" of any container.
        "format": "best[ext=mp4]/best",
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
    '''
    Downloads the best audio‐only stream (often .m4a or .webm), without running
    a postprocessor (i.e., no conversion to MP3). This way, we avoid needing ffmpeg.
    '''
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


if __name__ == "__main__":
    print("Downloading best progressive MP4 (no merging)…")
    mp4_path = download_progressive_mp4(YOUTUBE_URL, OUTPUT_DIR)
    print(f"  → Saved MP4 Progressively to: {mp4_path}")

    print("Downloading best audio‐only (no MP3 conversion)…")
    audio_path = download_best_audio_without_conversion(YOUTUBE_URL, OUTPUT_DIR)
    print(f"  → Saved audio stream to: {audio_path}")

    print("\nDone. (If you need an actual .mp3, you must install ffmpeg and re-run with a postprocessor.)")
```

### What Changed

- **Progressive MP4**:  
  ```python
  "format": "best[ext=mp4]/best"
  ```
  This ensures yt-dlp will only grab a single “progressive” MP4 file (one that already has audio & video). No separate streams, no merging.

- **Audio‐Only Without Conversion**:  
  ```python
  "format": "bestaudio[ext=m4a]/bestaudio"
  ```
  This picks the highest‐bitrate M4A if available, otherwise the best audio of any container (often WebM/Opus). Because we do not specify a `postprocessor` to convert it to MP3, yt-dlp will just save whatever the container is (`.m4a` or `.webm`). You’ll end up with, for example, `Some Title.m4a`. No ffmpeg required.

---

## 2.1 If You Still Need a True “.mp3”

Without ffmpeg, you cannot convert YouTube’s audio stream (which is almost always delivered as Opus in a WebM container or AC-3/M4A) into a genuine MP3. If you absolutely must have an MP3 file, you have two choices:

1. **Install ffmpeg** (see Section 1 above) so that yt-dlp’s built-in `FFmpegExtractAudio` postprocessor can run.  
2. **Manually convert** the downloaded `*.m4a` or `*.webm` file to MP3 using a separate tool (for example, run a standalone `ffmpeg -i in.m4a -b:a 192k out.mp3` in your shell).

But if you install ffmpeg as described in Section 1, you can simply revert to something like this in your `download_best_mp3` function:

```python
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
```

---

### 2.2 If You Never Want to Call ffmpeg

Use the code in the “Progressive MP4” & “Audio‐Only Without Conversion” section above. You will end up with:

- A `.mp4` file that already has audio+video (no merging).  
- An audio file in its original container (likely `.m4a` or `.webm`).  

You can play these files in any modern media player. If a strict `.mp3` is not absolutely required, this is the simplest route.

---

## 3. Summary

1. **Best Practice** (and what we originally recommended):  
   - **Install ffmpeg** → keep your `{"format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", …}` + `FFmpegExtractAudio` for MP3.  
   - Pros: always get highest‐possible quality, in clean `.mp4` (merged) and `.mp3` (re‐encoded).  
   - Cons: requires that external dependency (ffmpeg).

2. **No-ffmpeg Workaround**:  
   - For **video**:  
     ```python
     "format": "best[ext=mp4]/best"
     ```  
     → downloads a single progressive MP4.  
   - For **audio**:  
     ```python
     "format": "bestaudio[ext=m4a]/bestaudio"
     ```  
     → downloads the best M4A (or fallback) without converting to MP3.  
   - Pros: no external programs needed.  
   - Cons: you do not get an actual `.mp3` (you get M4A or WebM).

Choose the option that best fits your setup. If you only need to avoid the “ffmpeg is not installed” error and don’t mind installing one small binary, **installing ffmpeg** is the fastest way to resume using the code you already have. If you cannot install anything extra, switch to a purely “progressive” format string as shown above.

Feel free to copy/paste either code snippet into your `youtube_downloader.py` and run. Once done, you’ll have:

- **Case A (with ffmpeg)** → `video.mp4` (highest adaptive quality merged) and `audio.mp3` (highest‐bitrate re-encoded).  
- **Case B (no ffmpeg)** → `video.mp4` (best progressive) and `audio.m4a` (or `.webm`) as your “audio‐only” file.  

Either way, yt-dlp will work—no more “merging” errors.
