# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""
Create the Recipes (Synched) database in Notion under 2.AREAS and add five recipe rows.

Usage:
  NOTION_API_KEY=... NOTION_PARENT_PAGE_ID=... uv run --script recipes/scripts/setup_notion.py

NOTION_PARENT_PAGE_ID: The page id of 2.AREAS (or the page under which the database should be created).
Outputs NOTION_DATABASE_ID for use in the recipes backend (.env or README-BACKEND.md).
"""

import os
import sys
from uuid import UUID

import httpx

NOTION_VERSION = "2022-06-28"
BASE = "https://api.notion.com/v1"

RECIPES = [
    {
        "name": "Easy Lentil Soup",
        "rating100": 80,
        "contents": "Earthy brown/green lentil soup, versatile, plain or garnished.",
        "md_path": "2026-02/easy-lentil-soup-recipe.md",
    },
    {
        "name": "Red Lentil Soup",
        "rating100": 100,
        "contents": "Turkish-style (mercimek corbasi), light, spicy, lemon finish.",
        "md_path": "2026-02/red-lentil-soup-recipe-with-video.md",
    },
    {
        "name": "Everyday Dal",
        "rating100": 100,
        "contents": "10-min dal: lentils, turmeric, ghee tempering, 5 ingredients.",
        "md_path": "2026-02/everyday-dal-recipe.md",
    },
    {
        "name": "Curried Red Lentil Soup",
        "rating100": 100,
        "contents": "Red lentils, cumin, coriander, curry, tomatoes, lime.",
        "md_path": "2026-02/curried-red-lentil-soup-recipe.md",
    },
    {
        "name": "Best Lentil Soup",
        "rating100": 90,
        "contents": "Hearty greens (kale), vegetables, cumin, vinegar finish.",
        "md_path": "2026-02/lentil-soup-recipe-love-and-lemons.md",
    },
]


def normalize_id(id_str: str) -> str:
    """Remove dashes from UUID for Notion API (optional; API accepts both)."""
    try:
        return str(UUID(id_str)).replace("-", "")
    except ValueError:
        return id_str.replace("-", "")


def main() -> int:
    api_key = os.environ.get("NOTION_API_KEY")
    parent_page_id = os.environ.get("NOTION_PARENT_PAGE_ID")
    if not api_key or not parent_page_id:
        print(
            "Set NOTION_API_KEY and NOTION_PARENT_PAGE_ID (2.AREAS page id).",
            file=sys.stderr,
        )
        return 1

    parent_page_id = normalize_id(parent_page_id)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }

    with httpx.Client(timeout=30.0) as client:
        # Create database under 2.AREAS
        create_db = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": "Recipes (Synched)"}}],
            "properties": {
                "Name": {"title": {}},
                "Stars": {"number": {}},
                "Rating100": {"number": {}},
                "Contents": {"rich_text": {}},
                "MdPath": {"rich_text": {}},
            },
        }
        r = client.post(f"{BASE}/databases", headers=headers, json=create_db)
        if r.status_code != 200:
            print(f"Create database failed: {r.status_code} {r.text}", file=sys.stderr)
            return 1
        db = r.json()
        database_id = db["id"]
        print(f"Created database: {database_id}", file=sys.stderr)

        # Create five rows
        for recipe in RECIPES:
            body = {
                "parent": {"database_id": database_id},
                "properties": {
                    "Name": {
                        "title": [
                            {"type": "text", "text": {"content": recipe["name"]}}
                        ]
                    },
                    "Stars": {"number": 0},
                    "Rating100": {"number": recipe["rating100"]},
                    "Contents": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": recipe["contents"]},
                            }
                        ]
                    },
                    "MdPath": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": recipe["md_path"]},
                            }
                        ]
                    },
                },
            }
            r = client.post(f"{BASE}/pages", headers=headers, json=body)
            if r.status_code != 200:
                print(
                    f"Create page failed for {recipe['name']}: {r.status_code} {r.text}",
                    file=sys.stderr,
                )
                return 1
            print(f"  Created row: {recipe['name']}", file=sys.stderr)

    print(database_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
