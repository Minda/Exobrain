#!/usr/bin/env python3
"""
Fetch YouTube video transcript using youtube-transcript-api.

Usage:
    python fetch_transcript.py <youtube-url-or-id> [--output-dir <dir>]

Saves transcript JSON directly to file (avoids passing large content through LLM).
Outputs only status and file path to stdout:
    {
        "success": true,
        "video_id": "...",
        "file_path": "transcripts/abc123.json"
    }
"""

import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
)


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from YouTube URL or return as-is if already an ID."""
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url_or_id):
        return url_or_id

    try:
        parsed = urlparse(url_or_id)
        host = (parsed.hostname or "").lower()

        if host in ("youtube.com", "www.youtube.com", "m.youtube.com"):
            if parsed.path == "/watch":
                params = parse_qs(parsed.query)
                if "v" in params and params["v"]:
                    return params["v"][0]
            if parsed.path.startswith("/embed/"):
                cand = parsed.path.split("/embed/", 1)[1]
                if re.match(r"^[a-zA-Z0-9_-]{11}$", cand):
                    return cand

        if host in ("youtu.be", "www.youtu.be"):
            cand = parsed.path.lstrip("/")
            if re.match(r"^[a-zA-Z0-9_-]{11}$", cand):
                return cand
    except Exception:
        pass

    return url_or_id


def fetch_transcript(video_id: str) -> dict:
    """Fetch transcript for a YouTube video."""
    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id, ("en",))

        transcript_data = fetched.to_raw_data()
        parts = [s.get("text", "").strip() for s in transcript_data if s.get("text")]
        transcript_text = " ".join(parts)

        return {
            "success": True,
            "video_id": video_id,
            "title": None,
            "transcript": transcript_text,
            "transcript_data": transcript_data,
        }

    except TranscriptsDisabled:
        return {"success": False, "video_id": video_id, "error": "Transcripts are disabled for this video."}
    except NoTranscriptFound:
        return {"success": False, "video_id": video_id, "error": "No transcript found for this video."}
    except VideoUnavailable:
        return {"success": False, "video_id": video_id, "error": "Video is unavailable or does not exist."}
    except RequestBlocked:
        return {"success": False, "video_id": video_id, "error": "Request blocked or too many requests. Try again later."}
    except Exception as e:
        return {"success": False, "video_id": video_id, "error": f"Unexpected error: {e}"}


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Usage: python fetch_transcript.py <youtube-url-or-id> [--output-dir <dir>]"}))
        sys.exit(1)

    # Parse arguments
    url_or_id = sys.argv[1]
    output_dir = "transcripts"  # default
    
    # Check for --output-dir flag
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    video_id = extract_video_id(url_or_id)
    result = fetch_transcript(video_id)

    if not result.get("success"):
        # On failure, just output the error (no large content)
        print(json.dumps({"success": False, "video_id": video_id, "error": result.get("error", "Unknown error")}))
        sys.exit(1)

    # Create output directory if needed
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save full transcript JSON to file
    file_path = output_path / f"{video_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Output only status and file path (NOT the transcript content)
    print(json.dumps({
        "success": True,
        "video_id": video_id,
        "file_path": str(file_path)
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
