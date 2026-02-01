# Agent Skills Discovery RFC Reference

## Overview

The Cloudflare Agent Skills Discovery RFC (https://github.com/cloudflare/agent-skills-discovery-rfc) proposes a standardized mechanism for discovering AI agent skills using the `.well-known` URI path pattern, following RFC 8615.

This creates a universal discovery endpoint that allows agents to automatically find and retrieve skills without prior configuration or manual searching.

## Key Concepts

### The Problem Being Solved

Currently, finding agent skills requires manual searching through:
- GitHub repositories
- Vendor documentation
- Social media
- User configuration files

There's no standard way to answer: "What skills does example.com publish?"

### The Solution: Predictable Discovery

Organizations can publish skills at a standardized location:
```
https://example.com/.well-known/skills/
```

This provides a single discovery endpoint for agents and tools to automatically find available skills.

## Technical Specification

### URI Structure

```
/.well-known/skills/
├── index.json                    # Required: Skills inventory
├── {skill-name}/                 # Individual skill directory
│   ├── SKILL.md                  # Required: Skill definition
│   ├── scripts/                  # Optional: Supporting scripts
│   ├── references/               # Optional: Documentation
│   └── assets/                   # Optional: Other resources
```

### Skill Naming Requirements

- **Length**: 1-64 characters
- **Characters**: Lowercase alphanumeric and hyphens only
- **Format**: No leading/trailing or consecutive hyphens
- **Examples**: `processing-pdfs`, `git-workflow`, `data-analysis`

### Index Format

The `index.json` file must contain:

```json
{
  "skills": [
    {
      "name": "processing-pdfs",
      "description": "Extract and manipulate PDF content including text extraction, page splitting, and metadata analysis",
      "files": [
        "processing-pdfs/SKILL.md",
        "processing-pdfs/scripts/extract.py",
        "processing-pdfs/references/api-docs.md"
      ]
    }
  ]
}
```

Required fields:
- `name`: Skill identifier matching the directory name
- `description`: Brief usage guidance (≤1024 characters)
- `files`: Complete file listing for prefetching

## Progressive Disclosure Model

Skills load contextually across three levels to minimize context usage:

1. **Index Metadata** (~100 tokens per skill)
   - Name and description from index.json
   - Loaded when enumerating available skills

2. **Full Instructions** (<5000 tokens)
   - Complete SKILL.md content
   - Loaded when skill is activated

3. **Supporting Resources** (on-demand)
   - Scripts, references, assets
   - Fetched only when specifically needed

## Implementation Requirements

### For Skill Publishers

1. **Create the directory structure** at `/.well-known/skills/`
2. **Provide comprehensive index.json** with all skills listed
3. **Include complete file listings** for client prefetching
4. **Follow naming conventions** strictly
5. **Keep SKILL.md concise** (under 5000 tokens)
6. **Use relative paths** within skill directories

### For Client Implementations

Clients must:
1. **Fetch the index** to enumerate available skills
2. **Prefetch all files** for local caching
3. **Apply progressive disclosure** loading patterns
4. **Resolve relative paths** correctly
5. **Gate script execution** with user confirmation
6. **Respect HTTP cache headers** for efficiency

## Security Considerations

### Trust Boundaries
- Agents should only use skills from trusted origins
- Consider implementing an allowlist of skill sources
- Validate all file paths to prevent directory traversal

### Access Control
- The `/.well-known/skills/` path should be publicly accessible
- Individual skills may have additional authentication requirements
- Consider rate limiting to prevent abuse

### Script Execution
- All scripts must run in sandboxed environments
- Require explicit user confirmation before execution
- Log all script executions for audit purposes

### External Resources
- Validate all external URLs referenced in skills
- Consider blocking or warning about external resource access
- Cache external resources when possible

## Best Practices for Skill Creation

### When Creating Skills for Distribution

1. **Design for discoverability**
   - Write clear, searchable descriptions
   - Include relevant keywords
   - Specify exact use cases

2. **Follow the standard strictly**
   - Use the exact directory structure
   - Adhere to naming conventions
   - Include all required metadata

3. **Optimize for progressive disclosure**
   - Keep index descriptions concise but informative
   - Put detailed instructions in SKILL.md
   - Move extensive documentation to references/

4. **Version carefully**
   - Consider including version information in skill names or metadata
   - Document breaking changes
   - Maintain backwards compatibility when possible

### When Publishing Skills

1. **Test the discovery endpoint**
   ```bash
   curl https://yoursite.com/.well-known/skills/index.json
   ```

2. **Validate the structure**
   - Ensure all files listed in index.json exist
   - Check that paths are relative and correct
   - Verify skill names match directory names

3. **Set appropriate cache headers**
   - Use reasonable TTL values
   - Consider using ETags for efficient updates
   - Balance freshness with performance

## Integration with Claude Code Skills

This RFC aligns well with Claude Code's skill system:

### Similarities
- Both use a SKILL.md file as the primary definition
- Both support progressive disclosure
- Both allow scripts and references
- Both use lowercase-hyphenated naming

### Differences
- RFC uses `.well-known` URI pattern for web discovery
- Claude Code uses local `.claude/skills/` directory
- RFC requires index.json for enumeration
- Claude Code uses filesystem discovery

### Future Convergence

Skills created for Claude Code could potentially:
1. Be published at `.well-known/skills/` endpoints
2. Include the required index.json for discovery
3. Follow both specifications simultaneously
4. Enable cross-platform skill sharing

## Example: Publishing a Claude Code Skill

To make a Claude Code skill discoverable via the RFC standard:

1. **Structure your skill** following both specifications
2. **Create an index.json** listing your skills
3. **Deploy to your web server** at `/.well-known/skills/`
4. **Test discovery** with agent tools

Example deployment:
```
yoursite.com/
└── .well-known/
    └── skills/
        ├── index.json
        └── processing-pdfs/
            ├── SKILL.md
            ├── scripts/
            └── references/
```

## References

- [Cloudflare Agent Skills Discovery RFC](https://github.com/cloudflare/agent-skills-discovery-rfc)
- [RFC 8615 - Well-Known URIs](https://datatracker.ietf.org/doc/html/rfc8615)
- [Claude Code Skills Documentation](https://docs.claude.com/skills)

## Implications for the Future

This standardization could enable:
- **Universal skill marketplaces** where agents can discover skills from any website
- **Automatic capability negotiation** between agents and services
- **Composable web services** that agents can orchestrate
- **Decentralized skill ecosystems** without central registries
- **Cross-platform compatibility** between different AI systems

The RFC represents a significant step toward making the web more agent-friendly and creating a universal plugin system for AI assistants.