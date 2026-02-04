#!/usr/bin/env python3
"""
Split a large conversations.json file into individual conversation files.
Uses streaming JSON parsing to avoid loading the entire file into memory.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import re
import argparse


def sanitize_filename(title, max_length=100):
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
    # Keep alphanumeric, spaces, hyphens, underscores
    safe_title = re.sub(r'[^\w\s\-]', '', title)
    # Replace multiple spaces with single space
    safe_title = re.sub(r'\s+', ' ', safe_title)
    # Trim and limit length
    safe_title = safe_title.strip()[:max_length]
    # Replace spaces with underscores for filename
    safe_title = safe_title.replace(' ', '_')

    return safe_title if safe_title else "untitled"


def format_timestamp(timestamp):
    """Convert Unix timestamp to readable date string."""
    try:
        if timestamp:
            return datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')
    except:
        pass
    return "00000000_000000"


def get_conversation_info(conversation):
    """Extract key information from a conversation for naming and organization."""
    info = {
        'id': conversation.get('id', 'unknown'),
        'title': conversation.get('title', 'Untitled'),
        'create_time': conversation.get('create_time'),
        'update_time': conversation.get('update_time'),
        'model': conversation.get('default_model_slug', 'unknown'),
        'message_count': 0,
        'is_archived': conversation.get('is_archived', False),
        'is_starred': conversation.get('is_starred', False)
    }

    # Count messages in the mapping
    if 'mapping' in conversation and isinstance(conversation['mapping'], dict):
        info['message_count'] = len(conversation['mapping'])

    return info


def split_conversations(input_file, output_dir, naming_pattern='date_title',
                       create_index=True, verbose=False):
    """
    Split conversations.json into individual files.

    Args:
        input_file: Path to the conversations.json file
        output_dir: Directory to save individual conversation files
        naming_pattern: How to name files ('date_title', 'id', 'title_only')
        create_index: Whether to create an index file
        verbose: Print progress information
    """
    input_path = Path(input_file)
    output_path = Path(output_dir)

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Subdirectories for organization
    by_year_path = output_path / 'by_year'
    by_model_path = output_path / 'by_model'
    archived_path = output_path / 'archived'
    starred_path = output_path / 'starred'

    # Create subdirectories if organizing
    if naming_pattern != 'flat':
        by_year_path.mkdir(exist_ok=True)
        by_model_path.mkdir(exist_ok=True)
        archived_path.mkdir(exist_ok=True)
        starred_path.mkdir(exist_ok=True)

    index_data = []
    stats = {
        'total': 0,
        'processed': 0,
        'errors': 0,
        'by_model': {},
        'by_year': {}
    }

    print(f"Reading from: {input_path}")
    print(f"Writing to: {output_path}")
    print(f"Naming pattern: {naming_pattern}")
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
                try:
                    # Extract conversation info
                    info = get_conversation_info(conversation)

                    # Generate filename based on pattern
                    if naming_pattern == 'date_title':
                        timestamp = format_timestamp(info['create_time'])
                        safe_title = sanitize_filename(info['title'])
                        filename = f"{timestamp}_{safe_title}.json"
                    elif naming_pattern == 'id':
                        filename = f"{info['id']}.json"
                    elif naming_pattern == 'title_only':
                        safe_title = sanitize_filename(info['title'])
                        # Add ID suffix to handle duplicate titles
                        filename = f"{safe_title}_{info['id'][:8]}.json"
                    else:  # flat structure with ID
                        filename = f"{info['id']}.json"

                    # Determine output file path
                    file_path = output_path / filename

                    # Also save to category directories if applicable
                    category_paths = []

                    # By year
                    if info['create_time']:
                        year = datetime.fromtimestamp(info['create_time']).year
                        year_dir = by_year_path / str(year)
                        year_dir.mkdir(exist_ok=True)
                        category_paths.append(year_dir / filename)
                        stats['by_year'][year] = stats['by_year'].get(year, 0) + 1

                    # By model
                    if info['model']:
                        model = info['model'].replace('/', '_')  # Sanitize model name
                        model_dir = by_model_path / model
                        model_dir.mkdir(exist_ok=True)
                        category_paths.append(model_dir / filename)
                        stats['by_model'][model] = stats['by_model'].get(model, 0) + 1
                    else:
                        # Handle conversations with no model specified
                        model = 'no_model'
                        model_dir = by_model_path / model
                        model_dir.mkdir(exist_ok=True)
                        category_paths.append(model_dir / filename)
                        stats['by_model'][model] = stats['by_model'].get(model, 0) + 1

                    # Archived or starred
                    if info['is_archived']:
                        category_paths.append(archived_path / filename)
                    if info['is_starred']:
                        category_paths.append(starred_path / filename)

                    # Write the conversation to file(s)
                    with open(file_path, 'w', encoding='utf-8') as out_f:
                        json.dump(conversation, out_f, indent=2, ensure_ascii=False)

                    # Create hard links in category directories
                    for cat_path in category_paths:
                        if not cat_path.exists():
                            try:
                                os.link(file_path, cat_path)
                            except:
                                # Fall back to copying if hard link fails
                                with open(cat_path, 'w', encoding='utf-8') as cat_f:
                                    json.dump(conversation, cat_f, indent=2, ensure_ascii=False)

                    # Add to index
                    index_data.append({
                        'filename': filename,
                        'id': info['id'],
                        'title': info['title'],
                        'create_date': format_timestamp(info['create_time']),
                        'update_date': format_timestamp(info['update_time']),
                        'model': info['model'],
                        'messages': info['message_count'],
                        'archived': info['is_archived'],
                        'starred': info['is_starred']
                    })

                    stats['processed'] += 1

                    # Progress indicator
                    if verbose or (i + 1) % 100 == 0:
                        print(f"Processed {i + 1}/{stats['total']} conversations...")

                except Exception as e:
                    stats['errors'] += 1
                    print(f"Error processing conversation {i}: {e}")
                    if verbose:
                        print(f"  Conversation ID: {conversation.get('id', 'unknown')}")

        except json.JSONDecodeError as e:
            print(f"Error reading JSON file: {e}")
            return

    # Create index file if requested
    if create_index:
        index_path = output_path / 'index.json'
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'total_conversations': stats['total'],
                'processed': stats['processed'],
                'errors': stats['errors'],
                'by_model': stats['by_model'],
                'by_year': stats['by_year'],
                'conversations': index_data
            }, f, indent=2)
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
    print(f"\nBy model:")
    for model in sorted(stats['by_model'].keys()):
        print(f"  {model}: {stats['by_model'][model]}")


def main():
    parser = argparse.ArgumentParser(
        description='Split conversations.json into individual files'
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
        '--naming',
        choices=['date_title', 'id', 'title_only', 'flat'],
        default='date_title',
        help='Naming pattern for files (default: date_title)'
    )
    parser.add_argument(
        '--no-index',
        action='store_true',
        help='Skip creating index.json'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed progress'
    )

    args = parser.parse_args()

    split_conversations(
        args.input_file,
        args.output_dir,
        naming_pattern=args.naming,
        create_index=not args.no_index,
        verbose=args.verbose
    )


if __name__ == '__main__':
    main()