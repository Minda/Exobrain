# Recipes

Recipe markdown files and the recipes index live here (repo root by default). See [DigitalBrain CLAUDE.md](../CLAUDE.md) for optional placement under `personal/` if you prefer private content.

- **Markdown**: Downloaded recipe articles (e.g. `YYYY-MM/recipe-name.md`) from the download-url skill script with `--output-dir recipes`.
- **Index**: `index.html` lists recipes, links to `.md` files, shows rating/100, one-line contents, and a star rating synced with Notion. List and stars are loaded from a small backend that reads the Notion database **Recipes (Synched)** under 2.AREAS.
- **Notion**: Each recipe is a row in the **Recipes (Synched)** database (Name, Stars, Rating100, Contents, MdPath). Archiving a row in Notion removes it from the index on reload.
- **Sync via MCP**: You can create and update the Notion database and rows using the Notion MCP in Cursor (no API key in env). See [README-BACKEND.md](README-BACKEND.md#syncing-to-notion-via-mcp).

See **[README-BACKEND.md](README-BACKEND.md)** for MCP sync and how to run the backend and open the index.
