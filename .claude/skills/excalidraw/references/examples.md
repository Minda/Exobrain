# Complete Examples Reference

Real-world diagram examples with complete JSON structures.

---

## Simple 3-Tier Architecture

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "claude-code-excalidraw-skill",
  "elements": [
    {
      "id": "user",
      "type": "ellipse",
      "x": 550,
      "y": 50,
      "width": 100,
      "height": 60,
      "strokeColor": "#1971c2",
      "backgroundColor": "#e7f5ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": { "type": 2 },
      "seed": 1,
      "version": 1,
      "versionNonce": 1,
      "isDeleted": false,
      "boundElements": [{ "type": "text", "id": "user-text" }],
      "updated": 1,
      "link": null,
      "locked": false,
      "angle": 0
    },
    {
      "id": "user-text",
      "type": "text",
      "x": 575,
      "y": 65,
      "width": 50,
      "height": 30,
      "text": "User",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "user",
      "originalText": "User",
      "lineHeight": 1.25,
      "strokeColor": "#1971c2",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 2,
      "version": 1,
      "versionNonce": 2,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false,
      "angle": 0
    },
    {
      "id": "frontend",
      "type": "rectangle",
      "x": 500,
      "y": 180,
      "width": 200,
      "height": 80,
      "strokeColor": "#1971c2",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": { "type": 3 },
      "seed": 3,
      "version": 1,
      "versionNonce": 3,
      "isDeleted": false,
      "boundElements": [{ "type": "text", "id": "frontend-text" }],
      "updated": 1,
      "link": null,
      "locked": false,
      "angle": 0
    },
    {
      "id": "frontend-text",
      "type": "text",
      "x": 505,
      "y": 195,
      "width": 190,
      "height": 50,
      "text": "React App\nFrontend",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "frontend",
      "originalText": "React App\nFrontend",
      "lineHeight": 1.25,
      "strokeColor": "#1971c2",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 4,
      "version": 1,
      "versionNonce": 4,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false,
      "angle": 0
    },
    {
      "id": "database",
      "type": "rectangle",
      "x": 500,
      "y": 340,
      "width": 200,
      "height": 80,
      "strokeColor": "#2f9e44",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": { "type": 3 },
      "seed": 5,
      "version": 1,
      "versionNonce": 5,
      "isDeleted": false,
      "boundElements": [{ "type": "text", "id": "database-text" }],
      "updated": 1,
      "link": null,
      "locked": false,
      "angle": 0
    },
    {
      "id": "database-text",
      "type": "text",
      "x": 505,
      "y": 355,
      "width": 190,
      "height": 50,
      "text": "PostgreSQL\nDatabase",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "database",
      "originalText": "PostgreSQL\nDatabase",
      "lineHeight": 1.25,
      "strokeColor": "#2f9e44",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 6,
      "version": 1,
      "versionNonce": 6,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false,
      "angle": 0
    },
    {
      "id": "arrow-user-frontend",
      "type": "arrow",
      "x": 600,
      "y": 110,
      "width": 0,
      "height": 70,
      "points": [[0, 0], [0, 70]],
      "strokeColor": "#1971c2",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 7,
      "version": 1,
      "versionNonce": 7,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false,
      "angle": 0,
      "elbowed": true,
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "arrow-frontend-database",
      "type": "arrow",
      "x": 600,
      "y": 260,
      "width": 0,
      "height": 80,
      "points": [[0, 0], [0, 80]],
      "strokeColor": "#2f9e44",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 8,
      "version": 1,
      "versionNonce": 8,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false,
      "angle": 0,
      "elbowed": true,
      "startArrowhead": null,
      "endArrowhead": "arrow"
    }
  ],
  "appState": {
    "gridSize": 20,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```

---

## Layout Patterns

### Vertical Flow (6 Rows)

```
Row 1 (y: 50-100):   Users, Entry Points
Row 2 (y: 180-230):  Frontend, Gateway, Load Balancer
Row 3 (y: 330-380):  Orchestration, API Layer
Row 4 (y: 480-530):  Services, Processors
Row 5 (y: 630-680):  Data Layer (Databases, Cache)
Row 6 (y: 780-830):  External Services

Columns: x = 100, 300, 500, 700, 900 (200px spacing)
Element size: 160-200px width, 80-90px height
```

### Horizontal Pipeline

```
Stage 1 (x: 100):   Input/Source
Stage 2 (x: 350):   Processing
Stage 3 (x: 600):   Transform
Stage 4 (x: 850):   Output/Sink
Stage 5 (x: 1100):  Storage

Vertical positions: y = 200, 350, 500 for parallel tracks
```

### Hub-and-Spoke

```
Center (x: 500, y: 350): Orchestrator/Event Bus

Radial positions (radius ~200px):
  Top:         (500, 150)
  Top-Right:   (650, 200)
  Right:       (700, 350)
  Bottom-Right:(650, 500)
  Bottom:      (500, 550)
  Bottom-Left: (350, 500)
  Left:        (300, 350)
  Top-Left:    (350, 200)
```

---

## Complexity Guidelines

| Complexity | Element Count | Recommendation |
|------------|---------------|----------------|
| Simple | 5-10 | Single diagram, no grouping |
| Medium | 10-25 | Add grouping rectangles |
| Complex | 25-50 | Consider splitting by domain |
| Very Complex | 50+ | Split into focused diagrams |

**When to split:**
- More than 50 elements
- More than 3 distinct domains
- Diagram becomes cluttered
- Arrows cross multiple times

---

## Grouping Example

```json
{
  "id": "group-backend",
  "type": "rectangle",
  "x": 80,
  "y": 460,
  "width": 450,
  "height": 200,
  "strokeColor": "#7048e8",
  "backgroundColor": "transparent",
  "strokeStyle": "dashed",
  "strokeWidth": 1,
  "roughness": 0,
  "roundness": null,
  "boundElements": null
},
{
  "id": "group-backend-label",
  "type": "text",
  "x": 100,
  "y": 470,
  "text": "Backend Services",
  "fontSize": 14,
  "textAlign": "left",
  "containerId": null
}
```
