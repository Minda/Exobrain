# Recipes backend

The recipes index page loads the list and star ratings from Notion. You can sync to Notion in two ways:

- **MCP (recommended)** — Use the Notion MCP in Cursor to create the Recipes (Synched) database, add rows, and update star ratings. No API key in env; the MCP is already connected to your Notion.
- **Backend** — Run the Python server when you want the index page to work in a browser (load list, click stars). The backend needs `NOTION_API_KEY` and `NOTION_DATABASE_ID`.

## Syncing to Notion via MCP

In Cursor, you can use the Notion MCP tools to:

1. **Create the database** — Create a database "Recipes (Synched)" under 2.AREAS with properties: Name (title), Section (rich text), Stars (number), Rating100 (number), Contents (rich text), MdPath (rich text). Use the MCP tool that creates databases, then create child pages/rows with the recipe data.
2. **Add or update recipe rows** — Use `notion-create-pages` with parent = the Recipes (Synched) database id, and properties for each recipe (Name, Section, Rating100, Contents, MdPath; Stars 0 or 1–5).
3. **Update star ratings** — Use `notion-update-page` with the recipe page id and `properties: { "Stars": N }` (1–5).

Load the Notion tools via ToolSearch ("notion search fetch") if needed; see the **fetching-notion-content** skill for how to search and fetch. For creating/updating pages, the writing-drafting-article skill references `notion-create-pages` and `notion-update-page`.

If you use MCP for setup, you still need the **database id** for the backend if you run it — get it from the Notion MCP after creating the database.

## Prerequisites

1. **Notion integration** with an API key ([My integrations](https://www.notion.so/my-integrations)).
2. **2.AREAS page** in your Notion workspace. Share it with your integration (or use a page under it).
3. **Recipes (Synched) database** in Notion. If you haven’t created it yet, run the setup script once (see below).

## One-time Notion setup (Python script alternative)

If you prefer not to use MCP, from the **project root** (DigitalBrain):

```bash
export NOTION_API_KEY="your_secret_..."
export NOTION_PARENT_PAGE_ID="<page_id_of_2.AREAS>"
uv run --script shared/recipes/scripts/setup_notion.py
```

- **NOTION_PARENT_PAGE_ID**: Open 2.AREAS in Notion, copy the page ID from the URL (`https://notion.so/.../<NOTION_PARENT_PAGE_ID>?v=...`).
- The script creates a database **Recipes (Synched)** under that page and adds recipe rows (with Section, e.g. Lentils). It prints **NOTION_DATABASE_ID** — save it for the backend.

Share the new database (or its parent 2.AREAS) with your integration.

## Run the backend

From the **project root**:

```bash
# Install backend deps (once)
uv pip install -r shared/recipes/requirements.txt

# Run server (set your Notion env vars)
export NOTION_API_KEY="your_secret_..."
export NOTION_DATABASE_ID="<database_id_from_setup>"
uvicorn shared.recipes.server:app --reload
```

Default URL: **http://127.0.0.1:8000**

- **GET /** or **/index.html** — recipes index (sections + list + star rating).
- **GET /recipes** — JSON list of recipes from Notion (each has section).
- **PATCH /recipes/:id/stars** — body `{ "stars": 1..5 }` to update your rating in Notion.

Open **http://127.0.0.1:8000/** in a browser. List and stars are loaded from Notion on every open; if you archive a recipe in Notion, it won’t appear on reload.
