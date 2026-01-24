---
name: importing-conversations
description: Import, index, and organize conversation histories from Claude, ChatGPT, and other LLMs into a searchable archive system. Use when user wants to import, process, or archive AI conversation exports.
allowed-tools: [Read, Write, Bash, Glob]
---

# Importing Conversations

Import, index, and organize conversation histories from Claude, ChatGPT, and other LLMs into a searchable archive system.

## Usage

This skill helps you:
1. Import conversation exports from various LLMs
2. Automatically extract metadata and generate summaries
3. Organize conversations by date and platform
4. Build a searchable index for quick retrieval
5. Keep conversations out of context unless explicitly needed

## Activation

Say things like:
- "Import my Claude conversations"
- "I have ChatGPT exports to process"
- "Help me archive my AI conversation history"
- "Set up conversation imports"
- "Process my LLM chat exports"

## Core Workflow

### Phase 1: Identify Export Format

First, I'll help you identify what format your exports are in:

1. **Claude exports** typically come as:
   - JSON files with a specific structure
   - Individual conversation files or bulk exports
   - May include metadata like timestamps and model info

2. **ChatGPT exports** usually are:
   - ZIP files containing conversations.json
   - Complex nested structure with "mapping" nodes
   - Include create_time as Unix timestamps

3. **Other formats** we can handle:
   - Markdown conversation logs
   - CSV exports
   - Custom JSON formats

### Phase 2: Prepare Import Environment

```bash
# Ensure conversations directory exists
mkdir -p conversations/{claude,chatgpt,other}

# Check if SQLite database exists
if [ ! -f conversations/index.db ]; then
    echo "Creating new conversation index..."
fi

# Set up Python environment if needed
cd python
uv pip install -r requirements.txt 2>/dev/null || echo "Dependencies ready"
```

### Phase 3: Analyze Export Structure

I'll examine your export file to understand its structure:

```python
import json
from pathlib import Path

def analyze_export(file_path: str):
    """Analyze export file structure."""
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Detect platform based on structure
    if "messages" in data and "model" in data:
        return "claude_single"
    elif isinstance(data, list) and all("messages" in c for c in data):
        return "claude_bulk"
    elif "mapping" in data:
        return "chatgpt"
    elif isinstance(data, list) and all("title" in c for c in data):
        return "chatgpt_bulk"
    else:
        return "unknown"
```

### Phase 4: Extract and Process Conversations

Based on the format, I'll extract individual conversations:

#### Claude Format Processing

```python
def process_claude_export(data, single=True):
    """Process Claude export format."""
    conversations = []

    if single:
        conversations = [data]
    else:
        conversations = data if isinstance(data, list) else data.get("conversations", [])

    for conv in conversations:
        processed = {
            "id": generate_id(conv),
            "platform": "claude",
            "messages": extract_claude_messages(conv),
            "metadata": {
                "model": conv.get("model", "unknown"),
                "created_at": conv.get("created_at"),
                "updated_at": conv.get("updated_at")
            }
        }
        yield processed

def extract_claude_messages(conv):
    """Extract messages from Claude format."""
    messages = []
    for msg in conv.get("messages", []):
        messages.append({
            "role": msg.get("role"),
            "content": msg.get("content") or msg.get("text", ""),
            "timestamp": msg.get("timestamp")
        })
    return messages
```

#### ChatGPT Format Processing

```python
def process_chatgpt_export(data):
    """Process ChatGPT export format."""
    conversations = data if isinstance(data, list) else [data]

    for conv in conversations:
        messages = extract_chatgpt_messages(conv)
        processed = {
            "id": generate_id(conv),
            "platform": "chatgpt",
            "messages": messages,
            "metadata": {
                "title": conv.get("title", "Untitled"),
                "create_time": conv.get("create_time"),
                "update_time": conv.get("update_time")
            }
        }
        yield processed

def extract_chatgpt_messages(conv):
    """Extract messages from ChatGPT's complex structure."""
    messages = []
    mapping = conv.get("mapping", {})

    # Build message tree
    for node_id, node in mapping.items():
        if "message" in node and node["message"]:
            msg = node["message"]
            content = ""
            if "content" in msg:
                parts = msg["content"].get("parts", [])
                content = " ".join(str(p) for p in parts)

            messages.append({
                "role": msg.get("role"),
                "content": content,
                "timestamp": msg.get("create_time")
            })

    # Sort by timestamp if available
    messages.sort(key=lambda x: x.get("timestamp", 0))
    return messages
```

### Phase 5: Generate Smart Summaries

I'll create intelligent summaries for each conversation:

```python
def generate_conversation_summary(processed_conv):
    """Generate summary and metadata for a conversation."""
    messages = processed_conv["messages"]

    # Extract key information
    summary = {
        "title": extract_title(messages),
        "summary": create_summary(messages),
        "tags": extract_tags(messages),
        "topics": extract_topics(messages),
        "key_insights": extract_insights(messages),
        "token_count": estimate_tokens(messages)
    }

    return summary

def create_summary(messages):
    """Create a concise summary of the conversation."""
    if not messages:
        return "Empty conversation"

    # Get first substantial user message
    first_user = next((m for m in messages if m["role"] == "user" and len(m["content"]) > 50), None)

    # Get last substantial exchange
    last_user = next((m for m in reversed(messages) if m["role"] == "user"), None)

    # Count key metrics
    total_messages = len(messages)
    user_messages = sum(1 for m in messages if m["role"] == "user")

    summary_parts = []

    if first_user:
        summary_parts.append(f"Started with: {first_user['content'][:200]}...")

    if last_user and last_user != first_user:
        summary_parts.append(f"Concluded with: {last_user['content'][:200]}...")

    summary_parts.append(f"Total exchanges: {user_messages} user messages, {total_messages} total")

    return "\n".join(summary_parts)

def extract_tags(messages):
    """Extract relevant tags based on content analysis."""
    all_text = " ".join(m["content"] for m in messages).lower()

    # Programming languages and frameworks
    tags = []
    tech_keywords = {
        "python": ["python", "pip", "django", "flask", "pandas", "numpy"],
        "javascript": ["javascript", "js", "node", "npm", "react", "vue", "angular"],
        "rust": ["rust", "cargo", "rustc", "tokio", "serde"],
        "database": ["sql", "postgres", "mysql", "sqlite", "mongodb"],
        "ai-ml": ["machine learning", "neural", "llm", "gpt", "claude", "embedding"],
        "web": ["html", "css", "api", "rest", "graphql", "frontend", "backend"],
        "devops": ["docker", "kubernetes", "ci/cd", "deployment", "aws", "cloud"],
        "testing": ["test", "pytest", "jest", "unit test", "integration"],
        "debugging": ["debug", "error", "exception", "stack trace", "troubleshoot"]
    }

    for tag, keywords in tech_keywords.items():
        if any(kw in all_text for kw in keywords):
            tags.append(tag)

    return tags[:5]  # Limit to 5 most relevant tags
```

### Phase 6: Store and Index

Save processed conversations with smart organization:

```python
def store_conversation(processed_conv, summary_data):
    """Store conversation with proper structure."""
    platform = processed_conv["platform"]
    conv_id = processed_conv["id"]

    # Determine date for organization
    date = extract_date(processed_conv)
    year_month = date.strftime("%Y-%m")

    # Create directory structure
    conv_dir = Path(f"conversations/{platform}/{year_month}")
    conv_dir.mkdir(parents=True, exist_ok=True)

    # Write summary file (lightweight, for browsing)
    summary_path = conv_dir / f"{conv_id}_summary.md"
    write_summary_markdown(summary_path, processed_conv, summary_data)

    # Write full conversation (complete data)
    full_path = conv_dir / f"{conv_id}_full.json"
    with open(full_path, 'w') as f:
        json.dump(processed_conv, f, indent=2)

    # Update SQLite index
    update_search_index(conv_id, platform, date, summary_data, str(full_path))

    return conv_id, summary_path, full_path
```

### Phase 7: Build Search Index

Create a powerful search index:

```python
def update_search_index(conv_id, platform, date, summary_data, full_path):
    """Update SQLite search index."""
    import sqlite3

    conn = sqlite3.connect("conversations/index.db")

    # Ensure table exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            platform TEXT,
            date DATE,
            title TEXT,
            summary TEXT,
            tags TEXT,
            topics TEXT,
            key_insights TEXT,
            file_path TEXT,
            tokens_estimate INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create full-text search index
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS conversations_fts
        USING fts5(
            id, title, summary, tags, topics, key_insights,
            content=conversations
        )
    """)

    # Insert conversation
    conn.execute("""
        INSERT OR REPLACE INTO conversations
        (id, platform, date, title, summary, tags, topics, key_insights, file_path, tokens_estimate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        conv_id,
        platform,
        date,
        summary_data["title"],
        summary_data["summary"],
        ",".join(summary_data["tags"]),
        ",".join(summary_data["topics"]),
        "\n".join(summary_data.get("key_insights", [])),
        full_path,
        summary_data["token_count"]
    ))

    conn.commit()
    conn.close()
```

## Import Progress Tracking

I'll show you progress as we import:

```python
def import_with_progress(export_file, platform):
    """Import conversations with progress tracking."""
    print(f"\n📦 Loading {platform} export: {export_file}")

    with open(export_file, 'r') as f:
        data = json.load(f)

    # Determine processor
    if platform == "claude":
        processor = process_claude_export
    elif platform == "chatgpt":
        processor = process_chatgpt_export
    else:
        raise ValueError(f"Unknown platform: {platform}")

    conversations = list(processor(data))
    total = len(conversations)

    print(f"📊 Found {total} conversations to import\n")

    imported = []
    errors = []

    for i, conv in enumerate(conversations, 1):
        try:
            # Generate summary
            summary = generate_conversation_summary(conv)

            # Store conversation
            conv_id, summary_path, full_path = store_conversation(conv, summary)

            imported.append(conv_id)

            # Progress update
            print(f"[{i}/{total}] ✅ {summary['title'][:50]}... ({conv_id})")

        except Exception as e:
            errors.append((i, str(e)))
            print(f"[{i}/{total}] ❌ Error: {e}")

    # Final report
    print(f"\n📈 Import Complete:")
    print(f"  • Imported: {len(imported)} conversations")
    print(f"  • Errors: {len(errors)}")
    print(f"  • Index: conversations/index.db")

    return imported, errors
```

## Searching Your Archive

Once imported, you can search your conversations:

```bash
# Search by keyword
sqlite3 conversations/index.db "SELECT id, title, date FROM conversations_fts WHERE conversations_fts MATCH 'rust error handling'"

# Find by date range
sqlite3 conversations/index.db "SELECT id, title FROM conversations WHERE date BETWEEN '2024-01-01' AND '2024-03-31'"

# List all tags
sqlite3 conversations/index.db "SELECT DISTINCT tags FROM conversations"

# Find high-value conversations (lots of tokens)
sqlite3 conversations/index.db "SELECT id, title, tokens_estimate FROM conversations WHERE tokens_estimate > 10000 ORDER BY tokens_estimate DESC"
```

## Privacy and Storage

- All conversations are stored locally in `conversations/`
- The directory is gitignored by default for privacy
- You can selectively share specific conversations
- Summaries are lightweight (2-3KB) for quick browsing
- Full conversations are preserved exactly as exported

## Next Steps

After importing, you can:
1. Create custom views of your conversation history
2. Build topic-specific collections
3. Extract patterns and insights across conversations
4. Generate learning documents from past discussions
5. Find and reference specific solutions you've discussed before

The goal is to turn your conversation history into a searchable knowledge base that enhances your work with AI assistants without cluttering the active context.