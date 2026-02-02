# Advanced Skill Patterns

This guide covers six advanced patterns that distinguish polished, production-quality skills from basic ones. Each pattern includes the problem it solves, questions to ask when designing, and a full example using a hypothetical **"data-report-builder"** skill.

---

## 1. Progressive Disclosure / File Structure

**The problem:** Skills aren't flat documents. Loading everything into context every time wastes tokens and confuses Claude. Real skills keep the main SKILL.md lean and push detailed reference material into separate files that only get loaded when relevant.

**What to ask the person requesting the skill:**

> What information does Claude need *every single time* this skill runs vs. only in certain situations?

### Example — Directory structure

```
data-report-builder/
├── SKILL.md                    ← Always loaded. Core workflow, routing logic, ~200 lines max.
├── references/
│   ├── chart-guide.md          ← Loaded only when the report needs charts
│   ├── financial-formatting.md ← Loaded only for financial reports
│   ├── narrative-style.md      ← Loaded only when report includes written analysis
│   └── table-patterns.md       ← Loaded only when complex tables are involved
├── scripts/
│   ├── render_chart.py         ← Called to produce chart PNGs from data
│   └── validate_report.py      ← Called at the end to check the output
└── assets/
    ├── report-template.docx    ← Starting point for DOCX reports
    └── fonts/                  ← Bundled fonts for PDF output
```

### Example — What goes in SKILL.md (always loaded)

```markdown
# Data Report Builder

## Workflow
1. Identify report type (financial, operational, executive summary)
2. Load the appropriate reference:
   - Financial reports → read `references/financial-formatting.md`
   - Reports with charts → read `references/chart-guide.md`
   - Reports with narrative sections → read `references/narrative-style.md`
3. Process data and build report
4. Run validation

## Quick Reference
| Report type        | Reference to load            | Output format |
|--------------------|------------------------------|---------------|
| Financial          | financial-formatting.md      | XLSX + PDF    |
| Executive summary  | narrative-style.md           | DOCX          |
| Operational        | table-patterns.md            | PDF           |
```

### Example — What goes in a reference file (loaded on demand)

```markdown
# references/financial-formatting.md

## Number Formatting
- Currency: $#,##0 with units in headers ("Revenue ($mm)")
- Percentages: 0.0% (one decimal)
- Negative numbers: parentheses (123) not minus -123
- Zeros: display as "-"

## Color Coding
- Blue text: hardcoded inputs
- Black text: formulas
- Green text: cross-sheet links
...
```

**Why this matters:** Without this structure, either SKILL.md balloons to 500+ lines (wasting context on irrelevant details), or it's too sparse and Claude doesn't know where to find what it needs.

---

## 2. Bundled Scripts and Assets

**The problem:** Some operations are fragile, error-prone, or require exact sequences that Claude will get subtly wrong if asked to re-derive them. Bundling a tested script is more reliable and cheaper than having Claude write the code fresh each time.

**What to ask the person requesting the skill:**

> Which parts of this workflow are brittle enough that Claude should run a pre-written script instead of writing code from scratch? What operations does Claude reliably get wrong or produce inconsistently?

### Example — A script that Claude runs rather than recreates

```python
# scripts/render_chart.py
#
# Claude calls this script rather than writing matplotlib code each time.
# Why: Claude inconsistently handles DPI settings, font sizing relative to
# figure size, legend placement, and color-blind-safe palettes. This script
# encodes all of those decisions.

"""
Usage:
    python scripts/render_chart.py \
        --data input.csv \
        --chart-type bar \
        --title "Q3 Revenue by Region" \
        --output chart.png \
        --palette corporate \
        --size 8x5
"""

import argparse
import matplotlib.pyplot as plt
import pandas as pd

PALETTES = {
    "corporate": ["#1E2761", "#7A89C2", "#F96167", "#F9E795"],
    "muted":     ["#6C7B95", "#A8DADC", "#457B9D", "#E63946"],
    "mono":      ["#2D2D2D", "#5A5A5A", "#8C8C8C", "#BFBFBF"],
}

def render(data_path, chart_type, title, output, palette="corporate", size="8x5"):
    df = pd.read_csv(data_path)
    w, h = [float(x) for x in size.split("x")]
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)

    colors = PALETTES.get(palette, PALETTES["corporate"])

    # ... chart rendering logic with tested defaults for:
    #   - axis label sizing (12pt body, 14pt title)
    #   - tick rotation for long labels
    #   - legend placement (outside right if >4 series, inside otherwise)
    #   - grid lines (light gray, y-axis only)
    #   - tight_layout with pad=2.0

    fig.savefig(output, bbox_inches="tight", facecolor="white")
    plt.close(fig)
```

### Example — How SKILL.md references it

```markdown
## Charts

To add a chart to a report, use the bundled rendering script:

    python scripts/render_chart.py --data data.csv --chart-type bar --title "Title" --output chart.png

Supported chart types: bar, line, stacked_bar, pie, scatter.
Supported palettes: corporate, muted, mono.

Do NOT write matplotlib code directly. The script handles DPI, font
sizing, color accessibility, and layout consistency.
```

**Why this matters:** The script is tested, deterministic, and token-efficient. Claude calling it takes ~3 lines. Claude recreating equivalent logic takes ~80 lines and introduces subtle inconsistencies every time.

---

## 3. Workflow Branching

**The problem:** The basic template assumes a linear path: trigger → do steps → return result. Real skills need to route Claude to different workflows based on what the user actually needs.

**What to ask the person requesting the skill:**

> Does this skill handle different *types* of requests? Walk me through 3–4 different things a user might ask this skill to do, and how the approach differs for each.

### Example — Routing logic in SKILL.md

```markdown
## Workflow

### Step 1: Determine the task type

| User wants to...                        | Workflow         |
|-----------------------------------------|------------------|
| Create a report from raw data           | → Creation       |
| Update an existing report with new data | → Update         |
| Change the styling/format of a report   | → Restyle        |
| Analyze data and summarize findings     | → Analysis-first |

### Creation Workflow
1. Identify data sources (CSV, XLSX, or pasted data)
2. Determine report type (financial, operational, executive)
3. Load appropriate reference file
4. Build report structure
5. Generate charts with `scripts/render_chart.py`
6. Assemble final document
7. Validate with `scripts/validate_report.py`

### Update Workflow
1. Read existing report (unpack if DOCX, parse if PDF)
2. Identify which sections contain data-driven content
3. Replace data while preserving formatting and narrative
4. Re-render affected charts
5. Validate

### Restyle Workflow
1. Read existing report
2. Apply new template/theme (fonts, colors, layout)
3. Do NOT modify content or data
4. Validate visual output

### Analysis-First Workflow
1. Load and explore the data
2. Identify key patterns, outliers, trends
3. Draft narrative findings (load `references/narrative-style.md`)
4. THEN build the report around the findings
5. Validate
```

**Why this matters:** Without branching, Claude either follows the wrong workflow (rebuilding a report from scratch when the user just wanted a font change) or has to figure out the routing on its own (unreliable).

---

## 4. Output Verification

**The problem:** Basic templates only handle *input* errors — what if the user gives bad arguments. They never ask how Claude should verify that what it *produced* is actually correct.

**What to ask the person requesting the skill:**

> How would a human reviewer check that the output is correct? What are the most common ways this output can be subtly wrong?

### Example — Verification section in SKILL.md

```markdown
## Verification (Required)

Assume there are problems. Your job is to find them before delivering.

### Step 1: Content check
Run the content extractor and verify nothing is missing or duplicated:

    python -m markitdown output.docx | head -100

Check for:
- [ ] All sections from the outline are present
- [ ] No placeholder text remains ("TODO", "REPLACE", "Lorem ipsum")
- [ ] Numbers in tables match the source data
- [ ] Chart titles match their data

### Step 2: Formula check (if XLSX output)

    python scripts/recalc.py output.xlsx

If `status` is `errors_found`, fix every error before proceeding.
Common issues:
- `#REF!` → a cell reference points to a deleted row/column
- `#DIV/0!` → a denominator is zero; add an IFERROR wrapper
- `#VALUE!` → text in a cell that expects a number

### Step 3: Visual check
Convert to images and inspect:

    python scripts/office/soffice.py --headless --convert-to pdf output.docx
    pdftoppm -jpeg -r 150 output.pdf page

Review each page image for:
- [ ] No text overlapping other text or running off the page
- [ ] Charts are legible (labels not cut off, legends visible)
- [ ] Consistent margins and spacing
- [ ] Tables don't break awkwardly across pages

### Step 4: Fix-and-verify loop
If any issues are found:
1. Fix the issue
2. Re-run the check that caught it
3. Repeat until a full pass reveals no new issues

Do not deliver until at least one clean pass completes.
```

**Why this matters:** Claude's first output is almost never flawless. Without explicit verification steps, subtle errors (misaligned columns, placeholder text left in, off-by-one in data references) ship to the user unnoticed.

---

## 5. Craftsmanship / Quality Philosophy

**The problem:** Some skills need Claude to aim for a quality bar that's much higher than "technically correct." Creative and professional skills spend significant token budget on framing *expectations and standards* — not instructions per se, but a mindset shift.

**What to ask the person requesting the skill:**

> What does "excellent" look like for this output, beyond just being correct? Is there a quality bar, aesthetic standard, or professional expectation that matters?

### Example — Quality framing in SKILL.md

```markdown
## Quality Standards

### This is not a data dump
A report is not a spreadsheet with headers. It is a communication tool. Every element —
the title, the chart placement, the white space, the narrative flow — serves the reader's
understanding. If a section doesn't help the reader make a decision or grasp a trend,
remove it.

### Design principles
- **Hierarchy**: The most important finding should be visually dominant. Large numbers,
  bold callouts, or a chart placed above the fold. Secondary details recede.
- **Consistency**: Pick one font pairing, one color palette, and one table style.
  Use them everywhere. Inconsistency signals carelessness.
- **Breathing room**: Margins of at least 1 inch. 0.3–0.5 inches between content blocks.
  Cramped reports feel rushed. White space communicates confidence.
- **Narrative arc**: Executive summaries state the conclusion first, then the evidence.
  Not the other way around. The reader's time is more valuable than the data's completeness.

### The refinement pass
After assembling the report, re-read it as if the recipient is a board member
with five minutes. Ask:
- Can I grasp the main finding in under 10 seconds?
- Does every chart have a clear takeaway, not just data?
- Is there any section I'd skip? If so, cut or condense it.

Pretend the user has already said: "This needs to look like it came from a
top-tier consulting firm, not a script." Act accordingly.
```

**Why this matters:** Without this framing, Claude produces output that's functionally correct but generic — the equivalent of a plain white slide with bullet points. The philosophy section resets Claude's internal standard from "does it work" to "would I be proud of this."

---

## 6. Environmental Adaptation

**The problem:** Skills often need to behave differently depending on what tools, integrations, or context are available at runtime. Basic templates assume a fixed environment.

**What to ask the person requesting the skill:**

> Does this skill behave differently depending on what tools or integrations the user has available? Are there fallback paths if something isn't connected?

### Example — Adaptive workflow in SKILL.md

```markdown
## Data Source Detection

Before building the report, determine where the data is coming from and adapt:

### If the user uploads a file
- CSV/TSV: Load directly with pandas
- XLSX: Use openpyxl to preserve formatting context, or pandas for pure data
- JSON: Parse and flatten to tabular format

### If data integrations are available
Check for connected tools:

- **Google Sheets**: If available, ask the user for the sheet URL and pull data
  directly. This preserves named ranges and formatting context.
- **Database / SQL connector**: If available, ask the user for the query or table
  name. Run the query and load results. Prefer this over exported CSVs when fresh
  data matters.
- **Slack / email context**: If the user references a thread or message, pull the
  relevant data from the integration rather than asking them to copy-paste.

### If no data source is provided
Ask the user. Offer options in order of preference:
1. "Can you upload a CSV or spreadsheet?"
2. "Do you have a Google Sheet you can link?"
3. "You can paste the data directly into chat — I can work with that too."

Do NOT assume the data format. Always confirm before processing.

## Output Format Detection

### If the user has specified a format
Use it.

### If the user hasn't specified
- Reports with heavy data/tables → PDF (better table rendering)
- Reports needing future editing → DOCX
- Reports with interactive charts → HTML artifact

### If the user needs to share the report
Ask how:
- "Sharing as an email attachment" → PDF
- "Pasting into Google Docs" → DOCX
- "Posting to Slack/internal wiki" → PDF or markdown depending on platform

Adapt the output accordingly without making the user think about file formats.
```

**Why this matters:** Without environmental adaptation, the skill either assumes the best case (all integrations available) and fails when they're not, or assumes the worst case (nothing available) and ignores powerful tools the user has connected.

---

## Summary: Questions to Ask When Designing Skills

| Pattern | Key Question |
|---------|--------------|
| Progressive Disclosure | What does Claude need every time vs. only sometimes? |
| Bundled Scripts | What operations does Claude get wrong or inconsistent? |
| Workflow Branching | What different types of requests does this skill handle? |
| Output Verification | How would a human reviewer check the output is correct? |
| Quality Philosophy | What does "excellent" look like beyond "correct"? |
| Environmental Adaptation | What tools/integrations might be available or missing? |

Use these questions when gathering requirements for a new skill. The answers determine which patterns apply.
