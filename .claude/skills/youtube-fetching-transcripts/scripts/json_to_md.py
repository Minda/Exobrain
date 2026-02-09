#!/usr/bin/env python3
"""Convert JSON transcript to clean markdown with just text."""

import json
from pathlib import Path

def json_transcript_to_markdown(json_file, output_file=None):
    """Convert JSON transcript to markdown with only text content."""

    # Read JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract video ID for title
    video_id = data.get('video_id', 'unknown')

    # Build markdown content
    md_content = f"# YouTube Transcript: {video_id}\n\n"
    md_content += f"**Video URL:** https://www.youtube.com/watch?v={video_id}\n\n"
    md_content += "---\n\n"

    # Extract text from transcript_data
    # Join segments with spaces, add paragraph breaks for better readability
    transcript_segments = data.get('transcript_data', [])

    if transcript_segments:
        current_paragraph = []

        for i, segment in enumerate(transcript_segments):
            text = segment.get('text', '').strip()
            if text:
                current_paragraph.append(text)

                # Add paragraph break every ~5 segments or at natural pauses
                # (when there's a significant time gap or the text ends with punctuation)
                if (i + 1) % 5 == 0 or text.endswith(('.', '!', '?')):
                    if current_paragraph:
                        md_content += ' '.join(current_paragraph) + '\n\n'
                        current_paragraph = []

        # Add any remaining text
        if current_paragraph:
            md_content += ' '.join(current_paragraph) + '\n'

    else:
        # Fallback to 'transcript' field if no transcript_data
        transcript_text = data.get('transcript', '')
        if transcript_text:
            md_content += transcript_text

    # Determine output file
    if output_file is None:
        # Same name as input but with .md extension
        json_path = Path(json_file)
        output_file = json_path.parent / f"{json_path.stem}.md"

    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"✅ Converted: {json_file}")
    print(f"📄 Saved to: {output_file}")
    print(f"📊 Size: {len(md_content):,} characters")

    return output_file

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        # Default to the transcript we have
        json_file = "p4pHsuEf4Ms.json"

    json_transcript_to_markdown(json_file)