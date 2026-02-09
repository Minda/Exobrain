#!/usr/bin/env python3
"""Extract key information from transcript to create a descriptive filename."""

import json
import re
from pathlib import Path

def extract_title_from_transcript(json_file):
    """Extract the main topic/title from transcript content."""

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get the first few segments to identify the topic
    segments = data.get('transcript_data', [])[:20]  # First 20 segments
    text = ' '.join([seg.get('text', '') for seg in segments])

    # Look for key phrases that indicate the topic
    # The speaker mentions: "generative AI versus AI agents versus agentic AI"
    # And says this is about "basic differences between"

    # Extract the main topic from the introduction
    if 'generative AI versus' in text and 'AI agents versus agentic AI' in text:
        main_topic = "Generative AI vs AI Agents vs Agentic AI"
        short_name = "generative-ai-vs-ai-agents-vs-agentic-ai"
    else:
        # Fallback: look for other patterns
        main_topic = "AI Systems Comparison"
        short_name = "ai-systems-comparison"

    # Check if there's a speaker name
    speaker = None
    if 'my name is' in text.lower():
        match = re.search(r'my name is (\w+)', text, re.IGNORECASE)
        if match:
            speaker = match.group(1)

    # Create filename
    if speaker:
        filename_base = f"{short_name}-{speaker.lower()}"
        title = f"{main_topic} - {speaker}"
    else:
        filename_base = short_name
        title = main_topic

    return {
        'title': title,
        'filename_base': filename_base,
        'speaker': speaker,
        'topic': main_topic
    }

if __name__ == "__main__":
    import sys

    json_file = sys.argv[1] if len(sys.argv) > 1 else "p4pHsuEf4Ms.json"

    info = extract_title_from_transcript(json_file)

    print(f"Title: {info['title']}")
    print(f"Filename base: {info['filename_base']}")
    print(f"Speaker: {info['speaker']}")
    print(f"Topic: {info['topic']}")

    # Also save this info for reference
    with open('video_info.json', 'w') as f:
        json.dump(info, f, indent=2)