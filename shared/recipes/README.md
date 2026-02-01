# Recipes

General recipe list with sections. Lives under **shared/** (public repo content).

- **Markdown**: Recipe articles (e.g. `YYYY-MM/recipe-name.md`) from the download-url skill with `--output-dir shared/recipes`.
- **Index**: `index.html` lists recipes by section, links to `.md` files, shows rating/100, one-line contents, and star rating synced with Notion. List and stars come from a backend that reads the Notion database **Recipes (Synched)** under 2.AREAS.
- **Sections**: Each recipe can have a **Section** in Notion (e.g. Lentils, Soups); the index groups recipes by section.
- **Notion**: Each recipe is a row in **Recipes (Synched)** (Name, Section, Stars, Rating100, Contents, MdPath). Archiving a row in Notion removes it from the index on reload.
- **Sync via MCP**: Create and update the Notion database and rows using the Notion MCP in Cursor. See [README-BACKEND.md](README-BACKEND.md#syncing-to-notion-via-mcp).

See **[README-BACKEND.md](README-BACKEND.md)** for MCP sync and how to run the backend and open the index.
