#!/usr/bin/env python3
"""
Fetch YouTube video transcript using youtube-transcript-api.

Usage:
    python fetch_transcript.py <youtube-url-or-id>

Outputs JSON to stdout:
    {
        "success": true,
        "video_id": "...",
        "title": "...",  # if available
        "transcript": "Full transcript text...",
        "transcript_data": [...]  # Original segments with timestamps
    }
"""

import json
import re
import sys
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
        print(json.dumps({"success": False, "error": "Usage: python fetch_transcript.py <youtube-url-or-id>"}), file=sys.stderr)
        sys.exit(1)

    url_or_id = sys.argv[1]
    video_id = extract_video_id(url_or_id)
    result = fetch_transcript(video_id)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
