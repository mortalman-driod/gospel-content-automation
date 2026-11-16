"""
Viral Video Clipping Engine (src/clipper.py)
Automates the extraction and rendering of high-impact 90-second vertical video clips (9:16)
for TikTok, Instagram Reels, YouTube Shorts, and WhatsApp Status.

Pipeline:
1. Precision stream slicing via yt-dlp (--download-sections) without downloading full sermons.
2. 1080x1920 vertical canvas compositing via FFmpeg:
   - Zone A: Luxury editorial header (Speaker, Sermon/Song title, overline)
   - Zone B: 16:9 native video frame (1080x608) with gold borders
   - Zone C: Kinetic punchline / lyrics typography + Canonical scripture card
3. Preview extraction & artifact generation.
"""

import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger("kingdom_journal.clipper")
BASE_DIR = Path(__file__).resolve().parent.parent

class ViralClipperEngine:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (BASE_DIR / "output" / "clips")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.fonts_dir = BASE_DIR / "assets" / "fonts"

        # Resolve typography
        self.font_bold = self._resolve_font("Montserrat-Bold.ttf")
        self.font_regular = self._resolve_font("Poppins-Regular.ttf")
        self.font_serif = self._resolve_font("PlayfairDisplay-Bold.ttf")

    def _resolve_font(self, font_name: str) -> str:
        fp = self.fonts_dir / font_name
        if fp.is_file():
            # Format Windows path for FFmpeg filtergraph: forward slash and escaped colon
            return str(fp.resolve()).replace("\\", "/").replace(":", "\\:")
        return font_name

    @staticmethod
    def _format_time_hhmmss(seconds: int) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def download_slice(
        self,
        video_id_or_url: str,
        start_sec: int,
        duration_sec: int = 90,
        temp_filename: Optional[str] = None
    ) -> Optional[Path]:
        """
        Downloads only the specified time slice via yt-dlp.
        """
        if not video_id_or_url.startswith("http"):
            url = f"https://www.youtube.com/watch?v={video_id_or_url}"
            vid_id = video_id_or_url
        else:
            url = video_id_or_url
            m = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', video_id_or_url)
            vid_id = m.group(1) if m else "video"

        end_sec = start_sec + duration_sec
        t_start = self._format_time_hhmmss(start_sec)
        t_end = self._format_time_hhmmss(end_sec)

        temp_name = temp_filename or f"raw_{vid_id}_{start_sec}_{end_sec}.mp4"
        out_path = self.output_dir / temp_name

        cmd = [
            "yt-dlp",
            "--download-sections", f"*{t_start}-{t_end}",
            "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "--recode-video", "mp4",
            "-o", str(out_path),
            "--force-overwrites",
            url
        ]

        logger.info(f"Downloading slice {t_start} to {t_end} for {vid_id}...")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if out_path.is_file() and out_path.stat().st_size > 1000:
                logger.info(f"Successfully downloaded slice to {out_path} ({out_path.stat().st_size} bytes)")
                return out_path
            # Check webm or other container fallback
            for ext in [".webm", ".mkv"]:
                alt_path = out_path.with_suffix(ext)
                if alt_path.is_file() and alt_path.stat().st_size > 1000:
                    logger.info(f"Found downloaded slice at {alt_path} ({alt_path.stat().st_size} bytes)")
                    return alt_path
            if res.returncode != 0:
                logger.error(f"yt-dlp failed: {res.stderr}")
            return None
        except Exception as e:
            logger.error(f"Download exception: {e}")
            return None

    def _wrap_text(self, text: str, max_chars: int = 34) -> list:
        words = text.split()
        lines = []
        cur = []
        for w in words:
            if sum(len(x) for x in cur) + len(cur) + len(w) <= max_chars:
                cur.append(w)
            else:
                if cur:
                    lines.append(" ".join(cur))
                cur = [w]
        if cur:
            lines.append(" ".join(cur))
        return lines

    def render_vertical_short(
        self,
        raw_video_path: Path,
        output_name: str,
        speaker: str,
        title: str,
        quote: str,
        scripture_ref: str,
        scripture_text: str,
        duration_limit_sec: Optional[int] = 90
    ) -> Optional[Tuple[Path, Path]]:
        """
        Renders the 1080x1920 Triple-Deck vertical short and extracts a preview frame.
        Returns: (output_video_path, preview_image_path)
        """
        out_video = self.output_dir / f"{output_name}.mp4"
        out_preview = self.output_dir / f"{output_name}_preview.png"

        # Escape strings for FFmpeg drawtext
        def esc(s: str) -> str:
            return s.replace(":", "\\:").replace("'", "\\'").replace('"', '\\"').replace("%", "\\%")

        esc_speaker = esc(speaker.upper())
        esc_title = esc(title[:42])
        esc_scripture_ref = esc(f"SCRIPTURE ANCHOR • {scripture_ref.upper()}")
        esc_scripture_text = esc(f'"{scripture_text[:80]}"')

        # Format quote into 2-3 lines
        quote_lines = self._wrap_text(quote, max_chars=34)
        if len(quote_lines) > 4:
            quote_lines = quote_lines[:4]

        # Build dynamic drawtext filter chain
        filters = [
            "[0:v]scale=1080:608:force_original_aspect_ratio=decrease,pad=1080:608:(ow-iw)/2:(oh-ih)/2:color=black[vscaled]",
            "color=c=0x080c14:s=1080x1920:d=120[bg]",
            "[bg][vscaled]overlay=0:360[vbase]",
            # Gold borders
            "[vbase]drawbox=x=0:y=356:w=1080:h=4:color=0xd4af37@1.0:t=fill[vb1]",
            "[vb1]drawbox=x=0:y=968:w=1080:h=4:color=0xd4af37@1.0:t=fill[vb2]",
            # Header
            f"[vb2]drawtext=fontfile='{self.font_bold}':text='THE KINGDOM JOURNAL':fontcolor=0xd4af37:fontsize=22:x=(w-text_w)/2:y=120[vh1]",
            f"[vh1]drawtext=fontfile='{self.font_serif}':text='{esc_speaker}':fontcolor=0xffffff:fontsize=44:x=(w-text_w)/2:y=170[vh2]",
            f"[vh2]drawtext=fontfile='{self.font_regular}':text='{esc_title}':fontcolor=0x94a3b8:fontsize=26:x=(w-text_w)/2:y=240[vh3]",
        ]

        # Draw quote lines
        last_tag = "vh3"
        y_quote_start = 1040
        for idx, line in enumerate(quote_lines):
            next_tag = f"vq{idx}"
            col = "0xffe082" if idx % 2 == 1 else "0xffffff"
            filters.append(
                f"[{last_tag}]drawtext=fontfile='{self.font_bold}':text='{esc(line)}':fontcolor={col}:fontsize=38:x=(w-text_w)/2:y={y_quote_start + idx * 56}[{next_tag}]"
            )
            last_tag = next_tag

        # Draw scripture card
        filters.extend([
            f"[{last_tag}]drawbox=x=80:y=1380:w=920:h=220:color=0x131d2e@0.92:t=fill[vsc1]",
            "[vsc1]drawbox=x=80:y=1380:w=920:h=220:color=0xd4af37@0.65:t=2[vsc2]",
            f"[vsc2]drawtext=fontfile='{self.font_bold}':text='{esc_scripture_ref}':fontcolor=0xd4af37:fontsize=24:x=(w-text_w)/2:y=1420[vsc3]",
            f"[vsc3]drawtext=fontfile='{self.font_regular}':text='{esc_scripture_text}':fontcolor=0xffffff:fontsize=30:x=(w-text_w)/2:y=1480[vsc4]",
            f"[vsc4]drawtext=fontfile='{self.font_regular}':text='Daily Spiritual Fuel • 07\\:00 AM WAT':fontcolor=0x64748b:fontsize=20:x=(w-text_w)/2:y=1750"
        ])

        filter_graph = "; ".join(filters)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(raw_video_path),
            "-filter_complex", filter_graph,
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k",
        ]
        if duration_limit_sec:
            cmd.extend(["-t", str(duration_limit_sec)])
        cmd.append(str(out_video))

        logger.info(f"Rendering 9:16 vertical short to {out_video}...")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if res.returncode == 0 and out_video.is_file():
                # Extract preview frame at 3 seconds
                prev_cmd = ["ffmpeg", "-y", "-i", str(out_video), "-ss", "00:00:03", "-vframes", "1", str(out_preview)]
                subprocess.run(prev_cmd, capture_output=True)
                logger.info(f"Rendered short {out_video} and preview {out_preview}")
                return out_video, out_preview
            else:
                logger.error(f"FFmpeg render failed: {res.stderr[-1000:]}")
                return None
        except Exception as e:
            logger.error(f"Render exception: {e}")
            return None
