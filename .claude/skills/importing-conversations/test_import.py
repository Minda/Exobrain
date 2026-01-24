#!/usr/bin/env python3
"""
Test script for the importing-conversations skill.
Creates sample conversation data to test the import functionality.
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import random

def create_sample_claude_export():
    """Create a sample Claude export for testing."""
    messages = [
        {
            "role": "user",
            "content": "How do I implement error handling in Rust?",
            "timestamp": "2024-01-15T10:00:00Z"
        },
        {
            "role": "assistant",
            "content": "In Rust, error handling is done through the Result<T, E> type. Here are the main approaches:\n\n1. Using Result type\n2. The ? operator for propagation\n3. match expressions for handling\n4. unwrap() for prototyping (not recommended for production)",
            "timestamp": "2024-01-15T10:00:30Z"
        },
        {
            "role": "user",
            "content": "Can you show me an example with the ? operator?",
            "timestamp": "2024-01-15T10:01:00Z"
        },
        {
            "role": "assistant",
            "content": "Here's an example using the ? operator:\n\n```rust\nuse std::fs::File;\nuse std::io::{self, Read};\n\nfn read_username_from_file() -> Result<String, io::Error> {\n    let mut file = File::open(\"username.txt\")?;\n    let mut username = String::new();\n    file.read_to_string(&mut username)?;\n    Ok(username)\n}\n```\n\nThe ? operator automatically propagates errors up the call stack.",
            "timestamp": "2024-01-15T10:01:30Z"
        }
    ]

    return {
        "id": "test_conv_001",
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:02:00Z",
        "model": "claude-3-opus",
        "messages": messages
    }

def create_sample_chatgpt_export():
    """Create a sample ChatGPT export for testing."""
    # ChatGPT has a complex nested structure
    node1_id = "msg_001"
    node2_id = "msg_002"
    node3_id = "msg_003"
    node4_id = "msg_004"

    return {
        "title": "Python Async Programming",
        "create_time": 1705320000,  # Unix timestamp
        "update_time": 1705320120,
        "mapping": {
            node1_id: {
                "message": {
                    "role": "user",
                    "content": {
                        "parts": ["How do I use async/await in Python?"]
                    },
                    "create_time": 1705320000
                }
            },
            node2_id: {
                "message": {
                    "role": "assistant",
                    "content": {
                        "parts": ["Python's async/await syntax allows you to write asynchronous code. Here's how:\n\n1. Define async functions with `async def`\n2. Use `await` to call async functions\n3. Run with asyncio.run() or in an event loop"]
                    },
                    "create_time": 1705320030
                }
            },
            node3_id: {
                "message": {
                    "role": "user",
                    "content": {
                        "parts": ["Can you show me a practical example?"]
                    },
                    "create_time": 1705320060
                }
            },
            node4_id: {
                "message": {
                    "role": "assistant",
                    "content": {
                        "parts": ["Here's a practical example of fetching multiple URLs concurrently:\n\n```python\nimport asyncio\nimport aiohttp\n\nasync def fetch_url(session, url):\n    async with session.get(url) as response:\n        return await response.text()\n\nasync def main():\n    urls = ['http://example.com', 'http://google.com']\n    \n    async with aiohttp.ClientSession() as session:\n        tasks = [fetch_url(session, url) for url in urls]\n        results = await asyncio.gather(*tasks)\n    \n    return results\n\n# Run the async function\nresults = asyncio.run(main())\n```"]
                    },
                    "create_time": 1705320090
                }
            }
        }
    }

def create_bulk_sample():
    """Create multiple sample conversations for testing."""
    conversations = []

    # Generate 5 sample conversations
    topics = [
        ("Rust Memory Management", ["rust", "memory", "ownership"]),
        ("React Hooks Tutorial", ["javascript", "react", "frontend"]),
        ("Docker Deployment", ["docker", "devops", "deployment"]),
        ("SQL Query Optimization", ["database", "sql", "performance"]),
        ("Machine Learning Basics", ["ai-ml", "python", "data-science"])
    ]

    for i, (title, tags) in enumerate(topics):
        conv = {
            "id": f"bulk_conv_{i:03d}",
            "title": title,
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "messages": [
                {
                    "role": "user",
                    "content": f"Can you explain {title.lower()}?"
                },
                {
                    "role": "assistant",
                    "content": f"I'll help you understand {title.lower()}. Here are the key concepts..."
                }
            ]
        }
        conversations.append(conv)

    return conversations

def test_import_skill():
    """Test the import functionality."""
    print("🧪 Testing importing-conversations skill\n")

    # Create temporary directory for testing
    test_dir = Path("conversations_test")
    test_dir.mkdir(exist_ok=True)

    # Create sample exports
    claude_export = create_sample_claude_export()
    chatgpt_export = create_sample_chatgpt_export()
    bulk_export = create_bulk_sample()

    # Save test files
    test_files = []

    # Single Claude conversation
    claude_file = test_dir / "claude_test.json"
    with open(claude_file, 'w') as f:
        json.dump(claude_export, f, indent=2)
    test_files.append(("claude", claude_file))

    # Single ChatGPT conversation
    chatgpt_file = test_dir / "chatgpt_test.json"
    with open(chatgpt_file, 'w') as f:
        json.dump(chatgpt_export, f, indent=2)
    test_files.append(("chatgpt", chatgpt_file))

    # Bulk conversations
    bulk_file = test_dir / "bulk_test.json"
    with open(bulk_file, 'w') as f:
        json.dump(bulk_export, f, indent=2)
    test_files.append(("claude", bulk_file))

    print("✅ Created test files:")
    for platform, file_path in test_files:
        print(f"  - {file_path} ({platform})")

    print("\n📝 To test the import, run:")
    for platform, file_path in test_files:
        print(f"  python python/import_conversations.py {file_path} --platform {platform}")

    print("\n🔍 After import, test searches with:")
    print("  sqlite3 conversations/index.db \"SELECT id, title FROM conversations\"")
    print("  sqlite3 conversations/index.db \"SELECT * FROM conversations WHERE tags LIKE '%rust%'\"")

    print("\n🧹 Clean up test files with:")
    print(f"  rm -rf {test_dir}")

    return test_files

if __name__ == "__main__":
    test_import_skill()