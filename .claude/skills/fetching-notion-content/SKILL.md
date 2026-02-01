---
name: fetching-notion-content
description: Search and retrieve content from Notion workspace using MCP tools. Use when user asks to find, read, or reference Notion pages, databases, or notes. Triggers on "Notion", "find in Notion", "check my notes", "weekly report", or references to specific Notion pages.
allowed-tools: [ToolSearch, mcp__notion__notion-search, mcp__notion__notion-fetch]
---

# Fetching Notion Content

Search and retrieve content from the user's Notion workspace.

## Workspace Structure

This skill expects a PARA-inspired Notion organization:

- **1. PROJECTS** - Active projects with deadlines/goals
- **2. AREAS** - Ongoing areas of responsibility
- **3. RESOURCES** - Reference material and topic collections
- **4. LEARNING** - Courses, books, learning notes
- **0. JOURNALS** - Weekly reports, daily logs, reflections

**Key locations:**
- Projects are organized by quarter (e.g., "Q1: 2026")
- **Weekly Reports: 2026** - Active writing area where Substack drafts are developed

## Quick Start

1. **Load the Notion tools first** - Use ToolSearch to load `notion search fetch`
2. **Search** - Use `mcp__notion__notion-search` to find pages by semantic query
3. **Fetch** - Use `mcp__notion__notion-fetch` to get full page content

## Instructions

### Step 1: Load the Tools

The Notion MCP tools are deferred and must be loaded before use:

```
ToolSearch query: "notion search fetch"
```

This loads both `mcp__notion__notion-search` and `mcp__notion__notion-fetch`.

### Step 2: Search for Content

Use semantic search to find pages:

```json
{
  "query": "Week of Jan 26 - 30, 2026"
}
```

Search returns titles, URLs, highlights, and timestamps. Use the page ID or URL from results to fetch full content.

#### Search Options

- **Basic search**: Just provide a query string
- **Date filtering**: Add `filters.created_date_range` with `start_date` and/or `end_date`
- **User filtering**: Add `filters.created_by_user_ids` array
- **Search within page**: Add `page_url` to search within a specific page's subtree
- **Database search**: Add `data_source_url` with `collection://...` URL from a fetched database

### Step 3: Fetch Full Content

Use the page ID (with or without dashes) or full URL:

```json
{
  "id": "2f43caf3-73e0-80fa-8da8-f4d8478e839a"
}
```

Or:

```json
{
  "id": "https://www.notion.so/2f43caf373e080fa8da8f4d8478e839a"
}
```

Fetch returns:
- Page metadata and properties
- Full content in Notion-flavored markdown
- Child pages and databases as `<page url="...">` tags
- Images as `<image source="...">` tags

## Common Patterns

### Find and read a specific note
1. Search with descriptive query
2. Fetch the matching page by ID

### Find content from a time period
```json
{
  "query": "project updates",
  "filters": {
    "created_date_range": {
      "start_date": "2026-01-01",
      "end_date": "2026-02-01"
    }
  }
}
```

### Search within a database
1. First fetch the database to get the data source URL
2. Use that URL as `data_source_url` in search

## Guidelines

- Always load tools via ToolSearch before first use
- Search results include highlights - use these to confirm relevance before fetching
- For large pages, the content may be truncated - focus on the relevant sections
- Page IDs work with or without dashes
- If search returns no results, try broader or alternative query terms
