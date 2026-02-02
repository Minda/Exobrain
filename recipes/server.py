"""
Recipes backend: serves list from Notion and updates Stars on PATCH.

Run from project root:
  NOTION_API_KEY=... NOTION_DATABASE_ID=... uvicorn recipes.server:app --reload

Serves GET /recipes (list from Notion) and PATCH /recipes/:id/stars (update Stars).
Static files (index.html, *.md) are served from the recipes/ directory at /.
"""

import os
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

NOTION_VERSION = "2022-06-28"
BASE = "https://api.notion.com/v1"

app = FastAPI(title="Recipes Backend")

# Directory containing recipes (index.html, 2026-02/*.md)
RECIPES_DIR = Path(__file__).resolve().parent


def _notion_headers() -> dict:
    api_key = os.environ.get("NOTION_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="NOTION_API_KEY not set",
        )
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def _prop_title(prop: dict) -> str:
    if prop.get("type") != "title":
        return ""
    arr = prop.get("title") or []
    return "".join(
        (item.get("plain_text") or "") for item in arr
    ).strip()


def _prop_number(prop: dict) -> Optional[int]:
    if prop.get("type") != "number":
        return None
    v = prop.get("number")
    return int(v) if v is not None else None


def _prop_rich_text(prop: dict) -> str:
    if prop.get("type") != "rich_text":
        return ""
    arr = prop.get("rich_text") or []
    return "".join(
        (item.get("plain_text") or "") for item in arr
    ).strip()


@app.get("/recipes")
def get_recipes():
    """Return all non-archived recipe rows from the Notion database."""
    database_id = os.environ.get("NOTION_DATABASE_ID")
    if not database_id:
        raise HTTPException(
            status_code=500,
            detail="NOTION_DATABASE_ID not set",
        )
    database_id = database_id.replace("-", "")

    with httpx.Client(timeout=15.0) as client:
        r = client.post(
            f"{BASE}/databases/{database_id}/query",
            headers=_notion_headers(),
            json={"page_size": 100},
        )
        if r.status_code != 200:
            raise HTTPException(
                status_code=r.status_code,
                detail=r.text,
            )
        data = r.json()

    results = []
    for page in data.get("results", []):
        if page.get("archived"):
            continue
        props = page.get("properties") or {}
        # Property names from setup: Name, Stars, Rating100, Contents, MdPath
        name = ""
        stars = None
        rating100 = None
        contents = ""
        md_path = ""
        for key, prop in props.items():
            if prop.get("type") == "title":
                name = _prop_title(prop)
            elif key == "Stars":
                stars = _prop_number(prop)
            elif key == "Rating100":
                rating100 = _prop_number(prop)
            elif key == "Contents":
                contents = _prop_rich_text(prop)
            elif key == "MdPath":
                md_path = _prop_rich_text(prop)

        results.append({
            "id": page["id"],
            "title": name,
            "mdPath": md_path,
            "rating100": rating100 if rating100 is not None else 0,
            "contents": contents,
            "stars": stars if stars is not None else 0,
        })

    return results


class StarsUpdate(BaseModel):
    stars: int


@app.patch("/recipes/{page_id}/stars")
def update_stars(page_id: str, body: StarsUpdate):
    """Update the Stars property (1-5) for a recipe page in Notion."""
    if not (1 <= body.stars <= 5):
        raise HTTPException(status_code=400, detail="stars must be 1-5")
    page_id = page_id.replace("-", "")

    with httpx.Client(timeout=15.0) as client:
        r = client.patch(
            f"{BASE}/pages/{page_id}",
            headers=_notion_headers(),
            json={"properties": {"Stars": {"number": body.stars}}},
        )
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)

    return {"ok": True, "stars": body.stars}


# Serve static files from recipes/ at /
# index.html at / and /index.html; *.md under / (e.g. /2026-02/recipe.md)
app.mount("/", StaticFiles(directory=str(RECIPES_DIR), html=True), name="static")
