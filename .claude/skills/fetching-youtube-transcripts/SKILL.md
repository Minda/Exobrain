---
name: fetching-youtube-transcripts
description: Fetch transcript from YouTube video, save as JSON file (preserves timestamps and metadata), optionally create room and note, return file link. Use when user wants to extract or save YouTube video transcripts.
allowed-tools: [Read, Write, Bash]
---

# Fetching YouTube Transcripts

Fetch a YouTube video's transcript, save it as JSON, optionally store it in a "YouTube Transcripts" room as a Note, and return the file link.

## Quick Start

1. Get the YouTube URL or video ID from `$ARGUMENTS`.
2. Run the fetch script, save the JSON, optionally create a room/note, then return the path to the JSON file.

## Instructions

### 1. Parse input

- Read the YouTube URL or video ID from `$ARGUMENTS`.
- If empty or unclear, ask the user for a URL or video ID.

### 2. Fetch transcript

From the **workspace root**, run the fetch script so it can use the project's Python and `youtube-transcript-api`:

```bash
uv run --project python python .claude/skills/fetching-youtube-transcripts/scripts/fetch_transcript.py "<URL_OR_ID>"
```

If `uv` is not used, ensure the environment has `youtube-transcript-api` (e.g. `pip install -e ./python` or `youtube-transcript-api`) and run:

```bash
python .claude/skills/fetching-youtube-transcripts/scripts/fetch_transcript.py "<URL_OR_ID>"
```

- Capture stdout and parse JSON.
- If `success` is not true, report the `error` from the JSON and stop.

### 3. Save JSON

- From the JSON, take `video_id`.
- Create the `transcripts/` directory if it does not exist.
- Write the **entire** script output (full JSON) to `transcripts/<video_id>.json`.

### 4. (Optional) Create room and note

If the CLI (`mm`) is available and the user wants to store in the system:

```bash
mm room list 2>/dev/null | grep -qi "youtube transcripts" || mm room create "YouTube Transcripts" --description "Transcripts from YouTube videos"
```

Create a Note in the "YouTube Transcripts" room with the transcript text:

```bash
python -c "
import json, subprocess, sys
path = sys.argv[1]
d = json.load(open(path))
vid = d['video_id']
title = d.get('title') or ('YouTube Transcript: ' + vid)
subprocess.run(['mm', 'note', 'create', 'YouTube Transcripts', title, '-t', 'reference', '-c', d.get('transcript', '')], check=True)
" "transcripts/<video_id>.json"
```

Use the actual `transcripts/<video_id>.json` path. If the JSON has no `title`, use `"YouTube Transcript: " + video_id` as the note title.

### 5. Return the file link

Reply with the workspace-relative path to the JSON file:

```
./transcripts/<video_id>.json
```

Example:

```
Fetched transcript from YouTube video.
Saved to: ./transcripts/dQw4w9WgXcQ.json
```

## Error Handling

- **Invalid or missing URL/video ID**: Ask the user to provide a valid YouTube URL or 11‑character video ID.
- **Script reports failure**: Show the `error` from the JSON and stop; do not save JSON or create a Note.
- **Videos without transcripts**: The script returns `success: false` and an error; report it.
- **`mm` not found**: Skip the room/note creation step and just return the path to the JSON file.
- **`transcripts/` not writable**: Report the error and stop.

## File and JSON format

- File: `transcripts/<video_id>.json`
- The file holds the full JSON from the script:
  - `video_id`, `title` (if any), `transcript` (plain text), `transcript_data` (timestamped segments), `success`, and `error` when failed.

## Guidelines

- **Do** run the fetch script from the workspace root so the Python environment (with `youtube-transcript-api`) is used.
- **Do** save the full JSON (including `transcript_data`) to preserve timestamps and metadata.
- **Do** return a workspace-relative path like `./transcripts/<video_id>.json`.
- **Don't** change or trim the JSON before writing it to disk.
- **Don't** create the Note if the fetch failed (`success` is false).

## Example

**Input:** `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

**Output:**

```
Fetched transcript from YouTube video.
Saved to: ./transcripts/dQw4w9WgXcQ.json
```

The JSON file includes the full transcript text, timestamped segments, and video metadata.
