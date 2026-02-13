#!/usr/bin/env python3
"""Analyze the schema of a large conversations.json file."""

import json
from typing import Dict, Any, Set
from pathlib import Path


def analyze_schema(obj: Any, path: str = "root", depth: int = 0, max_depth: int = 5) -> Dict:
    """Recursively analyze the schema of a JSON object."""
    if depth > max_depth:
        return {"type": "...(max_depth_reached)"}

    if obj is None:
        return {"type": "null"}

    elif isinstance(obj, bool):
        return {"type": "boolean"}

    elif isinstance(obj, (int, float)):
        return {"type": "number"}

    elif isinstance(obj, str):
        return {"type": "string", "sample": obj[:50] if len(obj) > 50 else obj}

    elif isinstance(obj, list):
        if not obj:
            return {"type": "array", "items": "empty"}

        # Analyze first item as representative
        first_item_schema = analyze_schema(obj[0], f"{path}[0]", depth + 1, max_depth)
        return {
            "type": "array",
            "length": len(obj),
            "items": first_item_schema
        }

    elif isinstance(obj, dict):
        schema = {
            "type": "object",
            "properties": {}
        }

        for key in sorted(obj.keys()):
            schema["properties"][key] = analyze_schema(obj[key], f"{path}.{key}", depth + 1, max_depth)

        return schema

    else:
        return {"type": str(type(obj))}


def print_schema(schema: Dict, indent: int = 0):
    """Pretty print the schema."""
    spaces = "  " * indent

    if schema["type"] == "object":
        print(f"{spaces}object:")
        if "properties" in schema:
            for key, value in schema["properties"].items():
                print(f"{spaces}  {key}:", end="")
                if value["type"] not in ["object", "array"]:
                    if value["type"] == "string" and "sample" in value:
                        print(f" string (e.g., '{value['sample'][:30]}...')")
                    else:
                        print(f" {value['type']}")
                else:
                    print()
                    print_schema(value, indent + 2)

    elif schema["type"] == "array":
        length = schema.get("length", "unknown")
        print(f"{spaces}array[{length}]:")
        if "items" in schema and schema["items"] != "empty":
            print_schema(schema["items"], indent + 1)

    else:
        if schema["type"] == "string" and "sample" in schema:
            print(f" {schema['type']} (e.g., '{schema['sample'][:30]}...')")
        else:
            print(f" {schema['type']}")


def main():
    # Path to the conversations file
    file_path = Path("personal/conversational-history/conversations.json")

    print(f"Analyzing: {file_path}")
    print(f"File size: {file_path.stat().st_size / 1024 / 1024:.2f} MB")
    print()

    # Read and parse the JSON file
    with open(file_path, 'r') as f:
        data = json.load(f)

    print(f"Top-level type: {type(data).__name__}")

    if isinstance(data, list):
        print(f"Number of conversations: {len(data)}")
        print()

        if data:
            # Analyze the first conversation in detail
            print("Schema of first conversation:")
            print("-" * 50)
            schema = analyze_schema(data[0], max_depth=4)
            print_schema(schema)

            print("\n" + "=" * 50)
            print("\nKey insights:")
            print("-" * 50)

            # Collect all unique keys across conversations
            all_keys = set()
            mapping_keys = set()
            message_roles = set()

            for i, conv in enumerate(data[:min(100, len(data))]):  # Sample first 100
                if isinstance(conv, dict):
                    all_keys.update(conv.keys())

                    if "mapping" in conv and isinstance(conv["mapping"], dict):
                        for msg_id, msg_data in conv["mapping"].items():
                            if isinstance(msg_data, dict):
                                mapping_keys.update(msg_data.keys())

                                if "message" in msg_data and isinstance(msg_data["message"], dict):
                                    if "author" in msg_data["message"] and isinstance(msg_data["message"]["author"], dict):
                                        if "role" in msg_data["message"]["author"]:
                                            message_roles.add(msg_data["message"]["author"]["role"])

            print(f"\nTop-level conversation keys: {sorted(all_keys)}")
            print(f"\nMessage mapping keys: {sorted(mapping_keys)}")
            print(f"\nMessage roles found: {sorted(message_roles)}")

            # Sample some conversation titles
            print("\n\nSample conversation titles (first 10):")
            print("-" * 50)
            for i, conv in enumerate(data[:10]):
                if isinstance(conv, dict) and "title" in conv:
                    print(f"  {i+1}. {conv['title'][:60]}...")


if __name__ == "__main__":
    main()