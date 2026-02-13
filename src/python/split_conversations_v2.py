#!/usr/bin/env python3
"""
Split conversations.json into individual files with frontmatter metadata.
Each conversation becomes a single markdown file with YAML frontmatter.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import re
import argparse
import yaml


def sanitize_filename(title, max_length=80):
    """
    Create a safe filename from a conversation title.

    Args:
        title: The conversation title
        max_length: Maximum length for the filename

    Returns:
        A sanitized filename string
    """
    if not title or title.strip() == "":
        return "untitled"

    # Remove or replace problematic characters
    safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
    # Replace multiple spaces/underscores with single space
    safe_title = re.sub(r'[\s_]+', ' ', safe_title)
    # Trim and limit length
    safe_title = safe_title.strip()[:max_length]
    # Replace spaces with hyphens for filename
    safe_title = safe_title.replace(' ', '-')

    return safe_title if safe_title else "untitled"


def format_date(timestamp):
    """Convert Unix timestamp to readable date format."""
    try:
        if timestamp:
            dt = datetime.fromtimestamp(timestamp)
            # Format: "2024-03-18" for filename
            return dt.strftime('%Y-%m-%d')
    except:
        pass
    return "unknown-date"


def format_datetime(timestamp):
    """Convert Unix timestamp to full datetime for frontmatter."""
    try:
        if timestamp:
            return datetime.fromtimestamp(timestamp).isoformat()
    except:
        pass
    return None


def extract_conversation_text(conversation):
    """
    Extract the actual conversation text from the mapping structure.
    Returns a list of message exchanges.
    """
    messages = []
    mapping = conversation.get('mapping', {})

    # Build a tree structure to traverse messages in order
    # Find the root and traverse
    nodes_by_parent = {}
    for node_id, node_data in mapping.items():
        parent = node_data.get('parent')
        if parent not in nodes_by_parent:
            nodes_by_parent[parent] = []
        nodes_by_parent[parent].append((node_id, node_data))

    # Traverse from root
    def traverse_tree(node_id, depth=0):
        if node_id not in mapping:
            return

        node = mapping[node_id]
        message = node.get('message')

        if message and message.get('content'):
            author = message.get('author', {})
            role = author.get('role', 'unknown')

            # Skip system messages unless they contain meaningful content
            if role == 'system':
                metadata = message.get('metadata', {})
                if metadata.get('is_visually_hidden_from_conversation'):
                    # Skip hidden system messages
                    pass
                else:
                    # Include visible system messages
                    content = message.get('content', {})
                    if content.get('parts'):
                        text = '\n'.join(str(p) for p in content.get('parts', []) if p)
                        if text.strip():
                            messages.append({
                                'role': role,
                                'content': text,
                                'timestamp': message.get('create_time')
                            })
            else:
                # Regular user/assistant messages
                content = message.get('content', {})

                # Handle different content types
                if content.get('parts'):
                    text = '\n'.join(str(p) for p in content.get('parts', []) if p)
                elif content.get('text'):
                    text = content.get('text')
                elif content.get('content'):
                    text = content.get('content')
                else:
                    text = ""

                if text.strip():
                    messages.append({
                        'role': role,
                        'content': text,
                        'timestamp': message.get('create_time')
                    })

        # Traverse children
        children = node.get('children', [])
        for child_id in children:
            traverse_tree(child_id, depth + 1)

    # Start from root nodes
    root_nodes = nodes_by_parent.get(None, []) + nodes_by_parent.get('client-created-root', [])
    for node_id, _ in root_nodes:
        traverse_tree(node_id)

    return messages


def create_markdown_file(conversation, output_path):
    """
    Create a markdown file with frontmatter for a single conversation.

    Returns:
        Tuple of (success, filename, error_message)
    """
    try:
        # Extract metadata
        conv_id = conversation.get('id', 'unknown')
        title = conversation.get('title', 'Untitled Conversation')
        create_time = conversation.get('create_time')
        update_time = conversation.get('update_time')
        model = conversation.get('default_model_slug')
        is_archived = conversation.get('is_archived', False)
        is_starred = conversation.get('is_starred', False)

        # Count messages
        mapping = conversation.get('mapping', {})
        message_count = sum(1 for node in mapping.values()
                          if node.get('message') and
                          node.get('message', {}).get('author', {}).get('role') in ['user', 'assistant'])

        # Create filename: "2024-03-18 - Title of Conversation.md"
        date_str = format_date(create_time)
        safe_title = sanitize_filename(title)
        filename = f"{date_str} - {safe_title}.md"

        # Create frontmatter
        frontmatter = {
            'id': conv_id,
            'title': title,
            'created': format_datetime(create_time),
            'updated': format_datetime(update_time),
            'model': model,
            'message_count': message_count,
            'archived': is_archived,
            'starred': is_starred if is_starred is not None else False,
            'tags': []  # Can be expanded later
        }

        # Add model as a tag if it exists
        if model:
            frontmatter['tags'].append(f"model/{model}")

        # Extract conversation messages
        messages = extract_conversation_text(conversation)

        # Build the markdown content
        content_lines = []
        content_lines.append("---")
        content_lines.append(yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip())
        content_lines.append("---")
        content_lines.append("")
        content_lines.append(f"# {title}")
        content_lines.append("")

        # Add messages
        for msg in messages:
            role = msg['role'].upper()
            if role == 'USER':
                content_lines.append(f"## User")
            elif role == 'ASSISTANT':
                content_lines.append(f"## Assistant")
            else:
                content_lines.append(f"## {role.capitalize()}")

            content_lines.append("")
            content_lines.append(msg['content'])
            content_lines.append("")

        # Write the file
        file_path = output_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_lines))

        return True, filename, None

    except Exception as e:
        return False, None, str(e)


def split_conversations_markdown(input_file, output_dir, verbose=False):
    """
    Split conversations.json into individual markdown files with frontmatter.

    Args:
        input_file: Path to the conversations.json file
        output_dir: Directory to save individual conversation files
        verbose: Print progress information
    """
    input_path = Path(input_file)
    output_path = Path(output_dir)

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Create subdirectories for special categories only
    archived_path = output_path / 'archived'
    starred_path = output_path / 'starred'

    archived_path.mkdir(exist_ok=True)
    starred_path.mkdir(exist_ok=True)

    stats = {
        'total': 0,
        'processed': 0,
        'errors': 0,
        'by_year': {},
        'by_model': {}
    }

    index_data = []

    print(f"Reading from: {input_path}")
    print(f"Writing to: {output_path}")
    print()

    # Read and process the JSON file
    with open(input_path, 'r', encoding='utf-8') as f:
        try:
            conversations = json.load(f)
            stats['total'] = len(conversations)
            print(f"Found {stats['total']} conversations to process")
            print()

            # Process each conversation
            for i, conversation in enumerate(conversations):
                success, filename, error = create_markdown_file(conversation, output_path)

                if success:
                    stats['processed'] += 1

                    # Extract metadata for indexing
                    conv_id = conversation.get('id', 'unknown')
                    title = conversation.get('title', 'Untitled')
                    create_time = conversation.get('create_time')
                    model = conversation.get('default_model_slug', 'unknown')
                    is_archived = conversation.get('is_archived', False)
                    is_starred = conversation.get('is_starred', False)

                    # Track by year for statistics only
                    if create_time:
                        year = datetime.fromtimestamp(create_time).year
                        stats['by_year'][year] = stats['by_year'].get(year, 0) + 1

                    # Track by model
                    if model:
                        stats['by_model'][model] = stats['by_model'].get(model, 0) + 1

                    # Create symlinks for archived/starred
                    if is_archived:
                        source = Path('..') / filename
                        link = archived_path / filename
                        if not link.exists():
                            try:
                                link.symlink_to(source)
                            except:
                                pass

                    if is_starred:
                        source = Path('..') / filename
                        link = starred_path / filename
                        if not link.exists():
                            try:
                                link.symlink_to(source)
                            except:
                                pass

                    # Add to index
                    index_data.append({
                        'filename': filename,
                        'id': conv_id,
                        'title': title,
                        'date': format_date(create_time),
                        'model': model,
                        'archived': is_archived,
                        'starred': is_starred
                    })

                else:
                    stats['errors'] += 1
                    if verbose:
                        print(f"Error processing conversation {i}: {error}")

                # Progress indicator
                if (i + 1) % 100 == 0:
                    print(f"Processed {i + 1}/{stats['total']} conversations...")

        except json.JSONDecodeError as e:
            print(f"Error reading JSON file: {e}")
            return

    # Create index markdown file
    index_path = output_path / 'INDEX.md'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# Conversation Archive Index\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write(f"- **Total Conversations**: {stats['total']}\n")
        f.write(f"- **Successfully Processed**: {stats['processed']}\n")
        f.write(f"- **Errors**: {stats['errors']}\n\n")

        f.write("## By Year\n\n")
        for year in sorted(stats['by_year'].keys()):
            f.write(f"- **{year}**: {stats['by_year'][year]} conversations\n")

        f.write("\n## By Model\n\n")
        for model in sorted(stats['by_model'].keys(), key=lambda x: stats['by_model'][x], reverse=True)[:10]:
            f.write(f"- **{model}**: {stats['by_model'][model]} conversations\n")

        f.write("\n## All Conversations\n\n")
        f.write("| Date | Title | Model | Status |\n")
        f.write("|------|-------|-------|--------|\n")

        # Sort by date (newest first)
        sorted_convs = sorted(index_data, key=lambda x: x['date'], reverse=True)
        for conv in sorted_convs[:100]:  # Show first 100
            status = []
            if conv['archived']:
                status.append('📦')
            if conv['starred']:
                status.append('⭐')
            status_str = ' '.join(status) if status else '-'

            # Make title a link to the file
            title_link = f"[{conv['title']}]({conv['filename']})"
            f.write(f"| {conv['date']} | {title_link} | {conv['model'] or 'none'} | {status_str} |\n")

        if len(sorted_convs) > 100:
            f.write(f"\n*Showing first 100 of {len(sorted_convs)} conversations*\n")

    print(f"\nCreated index at: {index_path}")

    # Print summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Total conversations: {stats['total']}")
    print(f"Successfully processed: {stats['processed']}")
    print(f"Errors: {stats['errors']}")
    print(f"\nBy year:")
    for year in sorted(stats['by_year'].keys()):
        print(f"  {year}: {stats['by_year'][year]}")
    print(f"\nTop models:")
    for model in sorted(stats['by_model'].keys(), key=lambda x: stats['by_model'][x], reverse=True)[:5]:
        print(f"  {model}: {stats['by_model'][model]}")


def main():
    parser = argparse.ArgumentParser(
        description='Split conversations.json into markdown files with frontmatter'
    )
    parser.add_argument(
        'input_file',
        help='Path to conversations.json file'
    )
    parser.add_argument(
        'output_dir',
        help='Directory to save individual conversation files'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed progress'
    )

    args = parser.parse_args()

    split_conversations_markdown(
        args.input_file,
        args.output_dir,
        verbose=args.verbose
    )


if __name__ == '__main__':
    main()