---
name: excalidraw
description: Create valid .excalidraw diagram files with proper JSON structure, elements, arrows, and colors. Use when user wants to generate excalidraw files, create architecture diagrams, or visualize systems as excalidraw.
---

# Excalidraw Diagram Creator

Create valid `.excalidraw` JSON files for architecture diagrams, system visualizations, and flowcharts.

**This skill handles the HOW** — creating valid Excalidraw JSON. For analyzing what to diagram, see the `analyze-architecture` skill.

---

## Quick Start

When you have components to visualize:

1. Plan the layout (vertical flow, horizontal, or hub-and-spoke)
2. Create elements with proper shape + text pairing
3. Add arrows with correct edge calculations
4. Validate before writing
5. Save to `docs/` or user-specified path

---

## Critical Rules

### 1. NEVER Use Diamond Shapes

Diamond arrow connections are broken in raw Excalidraw JSON. Use styled rectangles instead:

| Semantic Meaning | Rectangle Style |
|------------------|-----------------|
| Orchestrator/Hub | Coral (`#ffa8a8`/`#c92a2a`) + strokeWidth: 3 |
| Decision Point | Orange (`#ffd8a8`/`#e8590c`) + dashed stroke |

### 2. Labels Require TWO Elements

The `label` property does NOT work in raw JSON. Every labeled shape needs:
- A shape with `boundElements` referencing a text element
- A text element with `containerId` referencing the shape

### 3. Elbow Arrows Need Three Properties

For 90-degree corners (not curved):

```json
{
  "type": "arrow",
  "roughness": 0,        // Clean lines
  "roundness": null,     // Sharp corners
  "elbowed": true        // 90-degree mode
}
```

### 4. Arrow Edge Calculations

Arrows must start/end at shape edges, not centers:

| Edge | Formula |
|------|---------|
| Top | `(x + width/2, y)` |
| Bottom | `(x + width/2, y + height)` |
| Left | `(x, y + height/2)` |
| Right | `(x + width, y + height/2)` |

---

## Element Types

| Type | Use For |
|------|---------|
| `rectangle` | Services, databases, containers, orchestrators |
| `ellipse` | Users, external systems, start/end points |
| `text` | Labels inside shapes, titles, annotations |
| `arrow` | Data flow, connections, dependencies |
| `line` | Grouping boundaries, separators |

---

## Default Color Palette

| Component | Background | Stroke |
|-----------|------------|--------|
| Frontend | `#a5d8ff` | `#1971c2` |
| Backend/API | `#d0bfff` | `#7048e8` |
| Database | `#b2f2bb` | `#2f9e44` |
| Storage | `#ffec99` | `#f08c00` |
| AI/ML | `#e599f7` | `#9c36b5` |
| External APIs | `#ffc9c9` | `#e03131` |
| Orchestration | `#ffa8a8` | `#c92a2a` |
| Message Queue | `#fff3bf` | `#fab005` |
| Cache | `#ffe8cc` | `#fd7e14` |
| Users | `#e7f5ff` | `#1971c2` |

---

## Layout Patterns

**Vertical flow (most common):**
```
Row 1: Users/Entry points (y: 100)
Row 2: Frontend/Gateway (y: 230)
Row 3: Orchestration (y: 380)
Row 4: Services (y: 530)
Row 5: Data layer (y: 680)

Columns: x = 100, 300, 500, 700, 900
Element size: 160-200px x 80-90px
```

---

## Quick Validation Checklist

Before writing file:
- [ ] Every shape with label has boundElements + text element
- [ ] Text elements have containerId matching shape
- [ ] Multi-point arrows have `elbowed: true`, `roundness: null`
- [ ] Arrow x,y = source shape edge point
- [ ] Arrow final point offset reaches target edge
- [ ] No diamond shapes
- [ ] No duplicate IDs

---

## Output

- **Location:** `personal/diagrams/` or user-specified (always in personal/ by default)
- **Filename:** Descriptive, e.g., `system-architecture.excalidraw`
- **Testing:** Open in https://excalidraw.com or VS Code extension

**Note:** All generated files save to `personal/` by default to keep the public repo clean.

---

## References

Detailed documentation in `references/`:
- `json-format.md` — Complete JSON structure
- `arrows.md` — Arrow routing algorithms
- `colors.md` — Platform-specific palettes (AWS, Azure, GCP, K8s)
- `examples.md` — Complete working examples
- `validation.md` — Validation algorithms and bug fixes
