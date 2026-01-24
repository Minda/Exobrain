#!/usr/bin/env python3
"""
Import and index conversation histories from Claude and ChatGPT exports.

This script is designed to work with the importing-conversations skill.

Usage:
    python import_conversations.py claude_export.json --platform claude
    python import_conversations.py chatgpt_export.json --platform chatgpt
    python import_conversations.py conversations.zip --platform chatgpt  # For ChatGPT data export
"""

import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
import re
import zipfile
import os


class ConversationImporter:
    def __init__(self, base_dir: Path = Path("conversations")):
        self.base_dir = base_dir
        self.base_dir.mkdir(exist_ok=True)
        self.db_path = self.base_dir / "index.db"
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with schema."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                date DATE NOT NULL,
                title TEXT,
                summary TEXT,
                tags TEXT,
                topics TEXT,
                file_path TEXT,
                tokens_estimate INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_date ON conversations(date);
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_platform ON conversations(platform);
        """)
        # Add full-text search
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS conversations_fts
            USING fts5(
                id, title, summary, tags, topics,
                content=conversations
            )
        """)
        conn.commit()
        conn.close()

    def import_conversation(self,
                          conv_data: Dict[str, Any],
                          platform: str) -> str:
        """Import a single conversation."""
        # Generate unique ID
        conv_id = self._generate_id(conv_data, platform)

        # Extract metadata
        date = self._extract_date(conv_data, platform)
        title = self._extract_title(conv_data, platform)
        summary = self._generate_summary(conv_data, platform)
        tags = self._extract_tags(conv_data)
        topics = self._extract_topics(conv_data)
        tokens = self._estimate_tokens(conv_data)

        # Create file paths
        year_month = date.strftime("%Y-%m")
        platform_dir = self.base_dir / platform / year_month
        platform_dir.mkdir(parents=True, exist_ok=True)

        summary_path = platform_dir / f"{conv_id}_summary.md"
        full_path = platform_dir / f"{conv_id}_full.json"

        # Write summary file
        self._write_summary(summary_path, {
            "id": conv_id,
            "date": date.isoformat(),
            "title": title,
            "summary": summary,
            "tags": tags,
            "topics": topics,
            "tokens": tokens,
            "full_path": str(full_path.relative_to(self.base_dir))
        })

        # Write full conversation
        with open(full_path, 'w') as f:
            json.dump(conv_data, f, indent=2)

        # Update database
        self._update_db(conv_id, platform, date, title, summary,
                       tags, topics, str(full_path), tokens)

        return conv_id

    def _generate_id(self, conv_data: Dict, platform: str) -> str:
        """Generate unique conversation ID."""
        # Use first message content + timestamp as unique identifier
        content = str(conv_data)[:500]  # First 500 chars
        timestamp = datetime.now().isoformat()
        hash_input = f"{platform}_{content}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:8]

    def _extract_date(self, conv_data: Dict, platform: str) -> datetime:
        """Extract conversation date based on platform format."""
        if platform == "claude":
            # Adjust based on actual Claude export format
            if "created_at" in conv_data:
                date_str = conv_data["created_at"]
                # Handle both with and without Z suffix
                if date_str.endswith('Z'):
                    date_str = date_str[:-1] + '+00:00'
                return datetime.fromisoformat(date_str)
        elif platform == "chatgpt":
            # Adjust based on actual ChatGPT export format
            if "create_time" in conv_data:
                return datetime.fromtimestamp(conv_data["create_time"])

        # Fallback to now
        return datetime.now()

    def _extract_title(self, conv_data: Dict, platform: str) -> str:
        """Extract or generate conversation title."""
        if "title" in conv_data:
            return conv_data["title"]

        # Generate from first message
        if platform == "claude" and "messages" in conv_data:
            first_msg = conv_data["messages"][0].get("text", "")[:100]
            return self._clean_title(first_msg)
        elif platform == "chatgpt" and "mapping" in conv_data:
            # Navigate ChatGPT's structure
            for node in conv_data["mapping"].values():
                if node.get("message", {}).get("role") == "user":
                    content = node["message"].get("content", {}).get("parts", [""])[0]
                    return self._clean_title(content[:100])

        return "Untitled Conversation"

    def _clean_title(self, text: str) -> str:
        """Clean text for use as title."""
        # Remove special characters, limit length
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:60] + "..." if len(text) > 60 else text

    def _generate_summary(self, conv_data: Dict, platform: str) -> str:
        """Generate conversation summary."""
        # This is a simplified version - you might want to use an LLM here
        messages = self._extract_messages(conv_data, platform)

        if not messages:
            return "No summary available"

        # Take first and last user messages for context
        user_messages = [m for m in messages if m.get("role") == "user"]
        if user_messages:
            first = user_messages[0].get("content", "")[:200]
            last = user_messages[-1].get("content", "")[:200] if len(user_messages) > 1 else ""
            return f"Started with: {first}\n\nEnded with: {last}" if last else f"Discussion about: {first}"

        return "Conversation between user and AI assistant"

    def _extract_messages(self, conv_data: Dict, platform: str) -> List[Dict]:
        """Extract messages in normalized format."""
        messages = []

        if platform == "claude":
            # Adjust based on actual format
            if "messages" in conv_data:
                messages = conv_data["messages"]
        elif platform == "chatgpt":
            # Navigate ChatGPT's node structure
            if "mapping" in conv_data:
                for node in conv_data["mapping"].values():
                    if "message" in node and node["message"]:
                        msg = node["message"]
                        messages.append({
                            "role": msg.get("role"),
                            "content": " ".join(msg.get("content", {}).get("parts", []))
                        })

        return messages

    def _extract_tags(self, conv_data: Dict) -> str:
        """Extract relevant tags from conversation."""
        # Simple keyword extraction - could be enhanced with NLP
        text = json.dumps(conv_data).lower()

        keywords = {
            "python": "python",
            "rust": "rust",
            "javascript": "javascript",
            "typescript": "typescript",
            "react": "react",
            "sql": "database",
            "api": "api",
            "debug": "debugging",
            "error": "error-handling",
            "test": "testing",
            "deploy": "deployment",
            "docker": "docker",
            "git": "git",
            "cli": "cli",
            "web": "web",
            "ai": "ai",
            "llm": "llm",
            "machine learning": "ml"
        }

        found_tags = []
        for keyword, tag in keywords.items():
            if keyword in text:
                found_tags.append(tag)

        return ",".join(found_tags[:5])  # Limit to 5 tags

    def _extract_topics(self, conv_data: Dict) -> str:
        """Extract main topics discussed."""
        # This is simplified - could use TF-IDF or LLM
        messages = self._extract_messages(conv_data, "")
        all_text = " ".join([m.get("content", "") for m in messages])

        # Look for capitalized phrases (often topics/proper nouns)
        topics = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', all_text)
        unique_topics = list(set(topics))[:10]

        return ",".join(unique_topics)

    def _estimate_tokens(self, conv_data: Dict) -> int:
        """Estimate token count for conversation."""
        # Rough estimate: 1 token ≈ 4 characters
        text = json.dumps(conv_data)
        return len(text) // 4

    def _write_summary(self, path: Path, metadata: Dict):
        """Write summary markdown file."""
        with open(path, 'w') as f:
            f.write(f"# {metadata['title']}\n\n")
            f.write(f"**Date:** {metadata['date']}\n")
            f.write(f"**ID:** {metadata['id']}\n")
            f.write(f"**Tags:** {metadata['tags']}\n")
            f.write(f"**Topics:** {metadata['topics']}\n")
            f.write(f"**Estimated tokens:** {metadata['tokens']:,}\n\n")
            f.write("## Summary\n\n")
            f.write(f"{metadata['summary']}\n\n")
            f.write("## Full Conversation\n\n")
            f.write(f"[View full conversation](./{metadata['full_path']})\n")

    def _update_db(self, conv_id: str, platform: str, date: datetime,
                   title: str, summary: str, tags: str, topics: str,
                   file_path: str, tokens: int):
        """Update SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO conversations
            (id, platform, date, title, summary, tags, topics, file_path, tokens_estimate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (conv_id, platform, date.date(), title, summary, tags, topics, file_path, tokens))
        conn.commit()
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Import conversation histories")
    parser.add_argument("file", help="Export file to import (JSON or ZIP)")
    parser.add_argument("--platform", choices=["claude", "chatgpt"], required=True,
                      help="Platform the export is from")
    parser.add_argument("--base-dir", default="conversations",
                      help="Base directory for conversations")
    parser.add_argument("--verbose", action="store_true",
                      help="Show detailed progress")

    args = parser.parse_args()

    # Handle different file types
    file_path = Path(args.file)
    data = None

    if file_path.suffix == '.zip':
        # Handle ChatGPT ZIP exports
        print(f"Extracting ZIP file: {file_path}")
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Look for conversations.json in the ZIP
            for name in zip_ref.namelist():
                if name.endswith('conversations.json'):
                    with zip_ref.open(name) as f:
                        data = json.load(f)
                    break
            if not data:
                print("Error: No conversations.json found in ZIP file")
                return
    else:
        # Regular JSON file
        with open(args.file, 'r') as f:
            data = json.load(f)

    # Initialize importer
    importer = ConversationImporter(Path(args.base_dir))

    # Handle different export formats
    conversations = []
    if args.platform == "claude":
        # Adjust based on actual Claude export structure
        if isinstance(data, list):
            conversations = data
        elif "conversations" in data:
            conversations = data["conversations"]
        else:
            conversations = [data]
    elif args.platform == "chatgpt":
        # ChatGPT typically exports as array
        if isinstance(data, list):
            conversations = data
        else:
            conversations = [data]

    # Import each conversation
    print(f"Importing {len(conversations)} conversations from {args.platform}...")

    for i, conv in enumerate(conversations, 1):
        try:
            conv_id = importer.import_conversation(conv, args.platform)
            print(f"[{i}/{len(conversations)}] Imported: {conv_id}")
        except Exception as e:
            print(f"[{i}/{len(conversations)}] Error: {e}")

    print(f"\nImport complete. Database: {importer.db_path}")


if __name__ == "__main__":
    main()