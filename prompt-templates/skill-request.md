# Skill Request

---

## 1. Overview

What will this skill do? Describe it in 2–3 sentences.
* Save learnings from each conversation for reference later
*

Trigger keywords: learning

---

## 2. Invocation

### Slash command
`/learning`

### Conversational triggers
What would a user say that should activate this skill?
* Can you save your main takeaways from this session?
* what have you learned in this session?

### Context triggers
What situation or file type should activate this skill automatically?
*
*

---

## 3. Arguments

| Argument | Description | Required? |
|----------|-------------|-----------|
| `$0` | _______________ | Yes / No |
| `$1` | _______________ | Yes / No |

Or freeform `$ARGUMENTS`: _______________

---

## 4. Workflow Shape

### Is this one linear path, or does the skill handle different types of requests?

Describe 1–4 different things a user might ask this skill to do, and how the approach differs for each.

| User wants to... | Workflow |
|-------------------|----------|
| review what they have learned together in this conversation | → review |
| load all stored memories into context | → load |
| load recent memories only | → recent |

### Workflow steps

For each workflow above (or just one if the skill is linear), list the steps:

**Workflow: review**
1a. take a deep breath, and when you are ready, go ahead and reflect on what you have learned in this session. You can jot down all of your thoughts at this step. Feel free to use anything that helps you think - emoji, ascii diagrams, tree diagrams, a mindmap. This step should mainly be able letting your thoughts flow. 
1b. Now take a couple of iterations to distill your learnings into concise insights. 
2. now go ahead and share this with the user as "today, I learned". You can use their name if you know it.
3. allow the user to reflect with you, ask questions, possibly dig deeper.
4. save this reflection to a file (e.g. `personal/learnings/YYYY-MM-DD-session-learnings.md`).
5. Return: a confirmation that the learning was saved, or if there were any errors with the save

**Workflow: load**
1. take a quick look at the files in personal/learnings/
2. make a second loop a closer look at the last three files in personal/learnings/
3. create a summary, using their name if available that warmly reviews what the two of you have learned together. Highlight some of the most recent memories and balance the existing ones.
4. Return: summary of learnings, highlighting the most recent

**Workflow: recent**
1. take a look at the last three files in personal/learnings/ 
2. make a second loop a closer look at the last three files in personal/learnings/ but don't overly load the context window up. 
3. create a summary, using their name if available that warmly reviews what the two of you have learned together recently.
4. Return: summary

<!--
WHY THIS SECTION EXISTS:
Real skills almost always branch. A PDF skill routes between read/create/edit/merge.
A report skill routes between creation/update/restyle. Without explicit routing,
Claude either follows the wrong workflow or guesses — unreliably.

Example:
| User wants to...                        | Workflow         |
|-----------------------------------------|------------------|
| Create a report from raw data           | → Creation       |
| Update an existing report with new data | → Update         |
| Change the styling/format of a report   | → Restyle        |

Creation Workflow:
1. Identify data sources
2. Determine report type (financial, operational, executive)
3. Load appropriate reference file
4. Build report structure
5. Generate charts
6. Validate
-->

---

## 5. Known Failure Modes

What does Claude reliably get wrong when attempting this task without guidance? Be specific — these should be concrete mistakes, not general advice.

| What Claude does wrong | What it should do instead |
|------------------------|--------------------------|
| _______________ | _______________ |
| _______________ | _______________ |
| _______________ | _______________ |

<!--
WHY THIS SECTION EXISTS:
Every mature skill has a catalog of specific pitfalls. These come from iteration
and are often the most valuable part of the skill. Examples from real skills:

- DOCX: Uses unicode bullets (•) instead of LevelFormat.BULLET numbering config
- DOCX: Uses \n for line breaks instead of separate Paragraph elements
- XLSX: Calculates values in Python and hardcodes them instead of using Excel formulas
- XLSX: Uses ShadingType.SOLID (causes black backgrounds) instead of ShadingType.CLEAR
- PPTX: Defaults to blue color scheme regardless of topic
- PPTX: Repeats the same layout on every slide
- Frontend: Converges on Inter/Roboto/Space Grotesk and purple gradients
- PDF: Uses unicode subscript characters that render as black boxes in ReportLab
-->

---

## 6. Guidelines

| Always | Never |
|--------|-------|
| _______________ | _______________ |
| _______________ | _______________ |

**Ask user if:** _______________

---

## 7. Error Handling

### Input errors

| Condition | Response |
|-----------|----------|
| _______________ | "_______________ " |
| _______________ | "_______________" |

### Output verification

How should Claude verify that what it produced is actually correct before delivering it? What are the most common ways the output can be subtly wrong?

**Content checks:**
- [ ] have you created a memory - concrete takeaways?
- [ ] how long is this memory? If it's still too long, try to distill the ideas further.

**Visual/structural checks:**
- [ ] _______________
- [ ] _______________

**Automated checks** (scripts, linters, validators to run):
- _______________
- _______________

Should Claude fix and re-verify in a loop? Yes

<!--
WHY THIS SECTION EXISTS:
Claude's first output is almost never flawless. Without explicit verification,
subtle errors ship unnoticed. Real skills mandate QA steps:

- PPTX: Convert slides to images, send to a subagent for visual inspection, then
  fix-and-verify in a loop until a clean pass completes.
- XLSX: Run recalc.py to recalculate all formulas, check for #REF!, #DIV/0!, etc.,
  fix every error, and re-run until status is "success."
- DOCX: Run `grep -iE "xxxx|lorem|ipsum"` to catch leftover placeholder text.

The instruction "Assume there are problems. Your job is to find them." appears
across multiple skills.
-->

---

## 8. Quality Standards

What does "excellent" look like for this output, beyond just being correct? Describe the quality bar, aesthetic standard, or professional expectation.

* concise takeaway that is easy to store and retreieve later, with deep contextual meaning.
*
*

### Degrees of freedom

How much creative latitude should Claude have?

- [ ] **Low** — Follow exact specifications. Consistency is critical. Deviation is a bug.
- [ ] **Medium** — Preferred patterns exist, but some adaptation to context is fine.
- [ X] **High** — Multiple approaches are valid. Claude should use judgment and be creative.

<!--
WHY THIS SECTION EXISTS:
Some skills need Claude to aim far above "technically correct." The creative skills
(canvas-design, algorithmic-art) spend significant tokens framing expectations:

  "Pretend the user has already said: 'This needs to look like it came from a
  top-tier consulting firm, not a script.' Act accordingly."

  "The user ALREADY said 'It isn't perfect enough. It must be pristine, a
  masterpiece of craftsmanship, as if it were about to be displayed in a museum.'"

Even non-creative skills benefit from this. A financial model skill might say:
"This is not a data dump. Every element serves the reader's understanding."

The degrees-of-freedom question comes from the skill-creator's own guidance:
narrow bridge with cliffs = low freedom, open field = high freedom.
-->

---

## 9. Environmental Adaptation

Does this skill behave differently depending on what tools, integrations, and context are available?

### Data sources / inputs
How should Claude get the data it needs? List in order of preference, with fallbacks.

| If available... | Then... |
|-----------------|---------|
| _______________ | _______________ |
| _______________ | _______________ |
| Nothing / unclear | Ask the user: "_______________ " |

### Output format
Should the output format adapt to the user's situation?

| Context | Preferred format |
|---------|-----------------|
| _______________ | _______________ |
| _______________ | _______________ |
| User hasn't specified | Default to: _______________ |

### Integration-dependent behavior
List any integrations that unlock different behavior (e.g., Slack, Google Drive, databases):

- If _______________ is available: _______________
- If _______________ is NOT available: _______________

<!--
WHY THIS SECTION EXISTS:
The doc-coauthoring skill detects whether Slack/Drive integrations are connected and
adapts: pull context directly if available, suggest enabling connectors if not, or
fall back to asking the user to paste content.

Without this, skills either assume the best case (all tools available) and fail,
or assume the worst case (nothing available) and ignore powerful tools.
-->

---

## 10. File Structure

### What information does Claude need every time vs. only sometimes?

**Always needed** (goes in SKILL.md — kept under ~200 lines):
- _______________
- _______________

**Needed only for specific sub-tasks** (goes in separate reference files):

| Reference file | Loaded when... |
|----------------|----------------|
| _______________ | _______________ |
| _______________ | _______________ |
| _______________ | _______________ |

### Scripts to bundle

Which operations should be pre-written scripts that Claude runs, rather than code Claude writes from scratch?

| Script | What it does | Why Claude shouldn't improvise this |
|--------|-------------|-------------------------------------|
| _______________ | _______________ | _______________ |
| _______________ | _______________ | _______________ |

### Assets to bundle

Templates, fonts, images, or other files the skill needs at runtime:

| Asset | Purpose |
|-------|---------|
| _______________ | _______________ |
| _______________ | _______________ |

### Resulting structure

```
skill-name/
├── SKILL.md
├── references/
│   ├── 
│   └── 
├── scripts/
│   ├── 
│   └── 
└── assets/
    ├── 
    └── 
```

<!--
WHY THIS SECTION EXISTS:
Skills are not flat documents. Every non-trivial skill in the repository uses
progressive disclosure: SKILL.md stays lean (~200 lines) and routes to reference
files loaded on demand. This keeps the context window focused.

Examples:
- PDF: SKILL.md covers basics, FORMS.md loaded only for form-filling, REFERENCE.md
  for advanced features.
- MCP-builder: SKILL.md has the workflow, four reference files loaded at different
  phases (best practices, Python guide, TypeScript guide, evaluation guide).
- Internal-comms: SKILL.md is a thin router, four example files loaded based on
  communication type (3P updates, newsletter, FAQ, general).

Scripts are often the core of the skill:
- DOCX: unpack.py, pack.py, comment.py, accept_changes.py
- XLSX: recalc.py for formula recalculation
- Web-artifacts-builder: init-artifact.sh, bundle-artifact.sh
- Slack-gif-creator: entire core/ library (gif_builder, validators, easing)

Assets provide fixed scaffolding:
- Algorithmic-art: viewer.html template
- Canvas-design: 40+ bundled font files
- Theme-factory: PDF showcase + 10 theme definition files
- Web-artifacts-builder: pre-packaged shadcn components
-->

---

## 11. Example Interaction

Show a complete example of this skill in action.

**User:** "_______________"

**Claude should:**
1. _______________
2. _______________
3. _______________
4. Verify: _______________
5. Return: _______________

---

## 12. Options

- [ ] **Manual only** — require `/slash-command` to invoke
- [X ] **Auto-invoke** — Claude activates when context matches (default)

## Example Interactions

**User:** `/learnings`
→ try to infer from context which workflow to use

**User:** `/learnings reflect`
→ use review workflow

**User:** `/learnings load`
→ use the load workflow and load all memories

**User:** `/learnings recent`
→ only load the most recent memories to spare the context window. 
