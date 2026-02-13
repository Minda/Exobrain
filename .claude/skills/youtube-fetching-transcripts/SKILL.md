---
name: youtube-fetching-transcripts
description: Fetch YouTube transcripts with optional custom directory, text-only markdown version, and content-based file naming. Preserves timestamps in JSON, creates clean markdown, and uses descriptive filenames.
allowed-tools: [Read, Write, Bash, Edit]
---

# Fetching YouTube Transcripts (Enhanced)

Fetch YouTube video transcripts with advanced features:
- Save to custom directories
- Create text-only markdown versions
- Rename files based on content (speaker, topic)
- Preserve full JSON with timestamps

## Arguments

| Argument | Description | Required? | Default |
|----------|-------------|-----------|---------|
| `$0` | YouTube URL or video ID | Yes | - |
| `$1` | Destination directory | No | Current directory |
| `$2` | Folder name for transcripts | No | "transcripts" |

## Quick Start

```bash
# Basic usage (saves to ./transcripts/)
/youtube-fetching-transcripts https://www.youtube.com/watch?v=abc123

# Custom directory and folder
/youtube-fetching-transcripts https://youtu.be/xyz789 /path/to/project videos

# Just custom directory (uses "transcripts" folder)
/youtube-fetching-transcripts https://youtu.be/xyz789 /path/to/project
```

## Instructions

### 1. Parse Arguments

```python
import sys

# Parse arguments from $ARGUMENTS
args = $ARGUMENTS.split()

# Extract components
url = args[0] if args else None
dest_dir = args[1] if len(args) > 1 else "."
folder_name = args[2] if len(args) > 2 else "transcripts"

# Construct full path
full_path = f"{dest_dir}/{folder_name}"
```

If no URL provided, ask user for YouTube URL or video ID.

### 2. Fetch Transcript to Custom Directory

Create the target directory and fetch transcript:

```bash
# Create directory structure
mkdir -p "$DEST_DIR/$FOLDER_NAME"

# Fetch transcript to custom location
uv run --project src/python python .claude/skills/youtube-fetching-transcripts/scripts/fetch_transcript.py "$URL" --output-dir "$DEST_DIR/$FOLDER_NAME"
```

Output example:
```json
{"success": true, "video_id": "p4pHsuEf4Ms", "file_path": "path/to/transcripts/p4pHsuEf4Ms.json"}
```

### 3. Create Text-Only Markdown Version

Convert JSON transcript to clean markdown (text only, no timestamps):

```bash
cd "$DEST_DIR/$FOLDER_NAME"
python .claude/skills/youtube-fetching-transcripts/scripts/json_to_md.py "$VIDEO_ID.json"
```

This creates a markdown file with just the text, organized into paragraphs.

### 4. Extract Content Information and Rename Files

Analyze transcript content to create descriptive filenames:

```bash
cd "$DEST_DIR/$FOLDER_NAME"
python .claude/skills/youtube-fetching-transcripts/scripts/extract_title.py "$VIDEO_ID.json"
```

This outputs:
```
Title: Generative AI vs AI Agents vs Agentic AI - Krishna
Filename base: generative-ai-vs-ai-agents-vs-agentic-ai-krishna
Speaker: Krishna
Topic: Generative AI vs AI Agents vs Agentic AI
```

Then rename both files:
```bash
mv "$VIDEO_ID.json" "$FILENAME_BASE.json"
mv "$VIDEO_ID.md" "$FILENAME_BASE.md"
```

### 5. Create or Update Index

If this is the first transcript in the folder, create README.md:

```bash
if [ ! -f "$DEST_DIR/$FOLDER_NAME/README.md" ]; then
    # Create new README with this transcript
    cat > "$DEST_DIR/$FOLDER_NAME/README.md" << EOF
# YouTube Transcripts

## Transcripts

### 1. $TITLE
- **Files:**
  - JSON: \`$FILENAME_BASE.json\`
  - Markdown: \`$FILENAME_BASE.md\`
- **Video ID:** $VIDEO_ID
- **URL:** https://www.youtube.com/watch?v=$VIDEO_ID
EOF
else
    # Append to existing README
    # (Add logic to append new transcript info)
fi
```

### 6. Open Created Files

Open the transcript files in the user's editor/viewer:

```bash
open "$DEST_DIR/$FOLDER_NAME/$FILENAME_BASE.md"
open "$DEST_DIR/$FOLDER_NAME/$FILENAME_BASE.json"
```

### 7. Report Results

Provide user with:
- Location of saved files
- Descriptive names used
- File sizes and content summary

Example output:
```
✅ YouTube Transcript Fetched and Processed

**Video:** Generative AI vs AI Agents vs Agentic AI - Krishna
**Location:** ./project/videos/

**Files Created:**
- `generative-ai-vs-ai-agents-vs-agentic-ai-krishna.json` (65 KB) - Full transcript with timestamps
- `generative-ai-vs-ai-agents-vs-agentic-ai-krishna.md` (16 KB) - Text-only version

**Content:** 17.7 minutes, 436 segments
**Topics:** Differences between Generative AI, AI Agents, and Agentic AI
```

## Scripts Included

### 1. `fetch_transcript.py`
- Fetches transcript from YouTube
- Supports custom output directories
- Returns JSON with timestamps and metadata

### 2. `json_to_md.py`
- Converts JSON transcript to markdown
- Removes timestamps, keeps only text
- Organizes into readable paragraphs

### 3. `extract_title.py`
- Analyzes transcript content
- Extracts speaker name and topic
- Generates descriptive filename

## Error Handling

| Error | Response |
|-------|----------|
| No transcript available | Report error, suggest checking if video has captions |
| Invalid URL/ID | Ask for valid YouTube URL or 11-character video ID |
| Directory creation fails | Check permissions, suggest alternative location |
| Python scripts fail | Provide fallback using video ID as filename |

## Workflow Decision Tree

```
User provides YouTube URL
├─ Arguments provided?
│  ├─ Yes: Parse destination and folder name
│  └─ No: Use defaults (./transcripts/)
├─ Fetch transcript to target directory
├─ Success?
│  ├─ Yes: Continue processing
│  └─ No: Report error and stop
├─ Create markdown version
├─ Extract title and rename files
├─ Update/create README index
└─ Open created files (md + json)
```

## Example Use Cases

### 1. Research Project
```bash
/youtube-fetching-transcripts https://youtu.be/abc123 ~/research/ai-papers conference-talks
```
Creates: `~/research/ai-papers/conference-talks/speaker-topic.json|md`

### 2. Content Collection
```bash
/youtube-fetching-transcripts https://youtube.com/watch?v=xyz789 downloads/courses lectures
```
Creates: `downloads/courses/lectures/professor-subject.json|md`

### 3. Default Behavior
```bash
/youtube-fetching-transcripts https://youtu.be/123
```
Creates: `./transcripts/content-based-name.json|md`

## Guidelines

- **Do** preserve original video ID in README for reference
- **Do** create both JSON (with timestamps) and MD (text-only) versions
- **Do** use descriptive filenames based on content
- **Don't** load full transcript into LLM context (too large)
- **Don't** overwrite existing files without confirmation