---
name: managing-cheatsheets
description: Maintain the cheatsheets index and organize cheatsheets into categories. Use when adding a new cheatsheet to the collection, creating categories, or reorganizing the index.
allowed-tools: [Read, Edit]
---

# Managing Cheatsheets

Maintain the cheatsheets index and organize cheatsheets into categories.

## When to Use

- Adding a new cheatsheet to the collection
- Creating a new cheatsheet category
- Reorganizing categories when they get too long
- Reviewing the index for consistency

## The Index

The main index lives at `cheatsheets/index.html`. It displays all cheatsheets organized by category.

## Adding a New Cheatsheet

1. **Create the cheatsheet file** in `cheatsheets/` (e.g., `tool-name.html`)
2. **Update the index** by adding an entry to the appropriate category section:

```html
<a href="your-cheatsheet.html" class="cheatsheet-item">
    <div class="icon">🔧</div>
    <div class="content">
        <h3>Tool Name</h3>
        <p>Brief one-line description</p>
    </div>
    <span class="arrow">→</span>
</a>
```

3. **Remove the empty state** placeholder if this is the first item in a category

## Current Categories

| Category | Purpose | CSS Color Variable |
|----------|---------|-------------------|
| **Agents** | AI agents, inference systems, autonomous systems | `--agents: #a855f7` |
| **Research** | Papers, academic concepts, studies | `--research: #4ecdc4` |
| **Tools** | Software, CLI, utilities | `--tools: #ffe66d` |
| **Concepts** | Patterns, methodologies, foundational ideas | `--concepts: #ff6b6b` |

## Creating a New Category

When existing categories don't fit:

1. **Add CSS color variable** in `:root`:
```css
--newcategory: #hexcolor;
```

2. **Add category styling** (icon background and header color):
```css
.category-newcategory .category-icon { background: rgba(r, g, b, 0.2); }
.category-newcategory h2 { color: var(--newcategory); }
```

3. **Add the section** in the HTML body:
```html
<section class="category category-newcategory">
    <div class="category-header">
        <div class="category-icon">🆕</div>
        <h2>New Category</h2>
    </div>
    <div class="cheatsheet-list">
        <!-- Cheatsheet items here -->
    </div>
</section>
```

## When to Reorganize

**Review the index when any category has 8+ items.**

Options:
- **Split into subcategories** — Add sub-headers within the category
- **Create more specific categories** — e.g., "Agents" → "Local Agents" + "Cloud Agents"
- **Merge sparse categories** — Combine categories with only 1-2 items each

**Principle:** Categories should be broad enough to hold 3-5+ items but not so broad they become meaningless lists.

## Cheatsheet File Guidelines

Each cheatsheet should be:
- **Self-contained** — Single HTML file with inline CSS
- **Consistent styling** — Dark theme, similar typography (JetBrains Mono + Space Grotesk)
- **Mobile-responsive** — Works on various screen sizes
- **No external dependencies** — Except Google Fonts

See existing cheatsheets for style reference.

## Commented Categories

The index has some categories commented out (Tools, Concepts). Uncomment them when you have content to add. This keeps the visible index clean.
