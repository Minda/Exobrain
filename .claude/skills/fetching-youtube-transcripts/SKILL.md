---
name: fetching-youtube-transcripts
description: Fetch transcript from YouTube video, save as JSON file (preserves timestamps and metadata), optionally create room and note, return file link. Use when user wants to extract or save YouTube video transcripts.
allowed-tools: [Read, Write, Bash]
---

# Fetching YouTube Transcripts

Fetch a YouTube video's transcript, save it as JSON, optionally store it in a "YouTube Transcripts" room as a Note, and return the file link.

**Important:** The script saves the transcript directly to a file. The transcript content does NOT pass through the LLM—only the status and file path are returned.

## Quick Start

1. Get the YouTube URL or video ID from `$ARGUMENTS`.
2. Run the fetch script (it saves the JSON directly).
3. Report the file path to the user.

## Instructions

### 1. Parse input

- Read the YouTube URL or video ID from `$ARGUMENTS`.
- If empty or unclear, ask the user for a URL or video ID.

### 2. Fetch and save transcript

From the **workspace root**, run the fetch script. The script automatically saves the transcript to `transcripts/<video_id>.json`:

```bash
uv run --project python python .claude/skills/fetching-youtube-transcripts/scripts/fetch_transcript.py "<URL_OR_ID>"
```

If `uv` is not used, ensure the environment has `youtube-transcript-api` and run:

```bash
python .claude/skills/fetching-youtube-transcripts/scripts/fetch_transcript.py "<URL_OR_ID>"
```

The script outputs a small JSON status (NOT the full transcript):

```json
{"success": true, "video_id": "abc123", "file_path": "transcripts/abc123.json"}
```

On failure:

```json
{"success": false, "video_id": "abc123", "error": "Error message"}
```

- If `success` is not true, report the `error` and stop.
- If `success` is true, the file has already been saved.

### 3. (Optional) Create room and note

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

### 4. Return the file link

Reply with the workspace-relative path to the JSON file:

```
Fetched transcript from YouTube video.
Saved to: ./transcripts/dQw4w9WgXcQ.json
```

## Error Handling

- **Invalid or missing URL/video ID**: Ask the user to provide a valid YouTube URL or 11‑character video ID.
- **Script reports failure**: Show the `error` from the JSON and stop.
- **Videos without transcripts**: The script returns `success: false` and an error; report it.
- **`mm` not found**: Skip the room/note creation step and just return the path to the JSON file.

## File and JSON format

- File: `transcripts/<video_id>.json`
- The file holds the full transcript data:
  - `video_id`, `title` (if any), `transcript` (plain text), `transcript_data` (timestamped segments), `success`

## Guidelines

- **Do** run the fetch script from the workspace root.
- **Do** let the script save the file directly—don't read or rewrite the transcript content.
- **Do** return a workspace-relative path like `./transcripts/<video_id>.json`.
- **Don't** read the transcript file content into the conversation (it may be very long).
- **Don't** create the Note if the fetch failed.

## Example

**Input:** `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

**Output:**

```
Fetched transcript from YouTube video.
Saved to: ./transcripts/dQw4w9WgXcQ.json
```

The JSON file includes the full transcript text, timestamped segments, and video metadata.
