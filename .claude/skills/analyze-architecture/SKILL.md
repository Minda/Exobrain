---
name: analyze-architecture
description: Analyze any project's architecture to identify components, services, databases, APIs, and data flows. Works with local codebases or GitHub repos. Use when user says "analyze architecture", "what's the structure of this project", or wants to understand a codebase before diagramming.
---

# Architecture Analyzer

Analyze any project — local or on GitHub — to identify components, services, relationships, and data flows.

**This skill handles the WHAT** — discovering what to diagram. For creating the actual diagram, see the `excalidraw` skill.

---

## Triggers

- "Analyze the architecture of this project"
- "What's the structure of [repo URL]?"
- "Map out the components in this codebase"
- "Understand this project before creating a diagram"

---

## Workflow

### Step 1: Determine Source

**Local project:**
```bash
# Check current directory structure
ls -la
# Look for key configuration files
```

**GitHub repo:**
```bash
# Clone to personal/repos/ for analysis
gh repo clone owner/repo personal/repos/repo-name
# Or use GitHub API for quick inspection without cloning
gh api repos/owner/repo/contents
```

**Note:** All cloned repos and analysis output save to `personal/` by default.

### Step 2: Identify Project Type

| Indicator | Project Type |
|-----------|-------------|
| `package.json` | Node.js / JavaScript |
| `Cargo.toml` | Rust |
| `pyproject.toml`, `requirements.txt` | Python |
| `go.mod` | Go |
| `docker-compose.yml` | Multi-service / Microservices |
| `terraform/`, `*.tf` | Infrastructure as Code |
| `k8s/`, `kubernetes/` | Kubernetes deployment |
| `packages/`, `apps/` | Monorepo |

### Step 3: Discover Components

**Look for these patterns:**

| Component Type | Where to Find |
|----------------|---------------|
| **Services** | `services/`, `apps/`, `packages/`, Docker Compose services |
| **APIs** | Route definitions, controllers, `api/`, OpenAPI specs |
| **Databases** | DB connection configs, migrations, models, schemas |
| **Message Queues** | Kafka/RabbitMQ/SQS configs, event handlers |
| **Cache** | Redis configs, cache middleware |
| **Frontend** | `src/`, `client/`, `web/`, `app/` with React/Vue/etc |
| **Workers** | Background job processors, cron configs |
| **External APIs** | HTTP client calls, SDK imports, API keys in env |

### Step 4: Map Relationships

**Data flow patterns:**

```
1. Entry points → What receives external requests?
2. Internal calls → Which services talk to which?
3. Data stores → What reads/writes to databases?
4. External deps → What calls third-party APIs?
5. Events → What publishes/subscribes to queues?
```

**Look for:**
- Import statements between modules
- HTTP/gRPC client configurations
- Database connection strings
- Queue publish/subscribe patterns
- Environment variables referencing other services

### Step 5: Output Analysis

Produce a structured summary:

```markdown
## Project: [name]

### Components

| Component | Type | Technology | Location |
|-----------|------|------------|----------|
| API Gateway | Backend | Express.js | `src/api/` |
| User Service | Backend | Node.js | `services/user/` |
| PostgreSQL | Database | PostgreSQL | Docker |
| Redis | Cache | Redis | Docker |
| React App | Frontend | React | `client/` |

### Relationships

- User → API Gateway: HTTP requests
- API Gateway → User Service: Internal API
- User Service → PostgreSQL: User data CRUD
- API Gateway → Redis: Session cache

### External Dependencies

- Stripe API (payments)
- SendGrid (email)
- AWS S3 (file storage)
```

---

## Analysis Strategies by Project Type

### Monorepo

```bash
# List all packages/apps
ls packages/ apps/
# Check workspace config
cat package.json | jq '.workspaces'
# Or pnpm-workspace.yaml, turbo.json
```

### Microservices (Docker Compose)

```bash
# Parse docker-compose.yml
cat docker-compose.yml
# Identify services, networks, dependencies
```

### Infrastructure as Code

```bash
# Terraform resources
grep -r "resource " terraform/*.tf
# Identify cloud services, databases, networking
```

### Backend API

```bash
# Find route definitions
grep -r "app.get\|app.post\|router\." src/
# Or for other frameworks
grep -r "@Get\|@Post\|@Controller" src/  # NestJS
grep -r "def get\|def post" app/         # Python
```

### Kubernetes

```bash
# List all K8s resources
ls k8s/*.yaml
# Identify deployments, services, ingresses
grep -r "kind:" k8s/
```

---

## GitHub Analysis (Remote)

For repos you don't want to clone:

```bash
# Get repo structure
gh api repos/owner/repo/contents --jq '.[].name'

# Get specific file
gh api repos/owner/repo/contents/docker-compose.yml \
  --jq '.content' | base64 -d

# Get directory contents
gh api repos/owner/repo/contents/src --jq '.[].name'

# Search for patterns
gh api "search/code?q=repo:owner/repo+filename:docker-compose"
```

---

## Output Format

When analysis is complete, present:

1. **Summary** — One paragraph describing the system
2. **Components table** — All identified components with type and tech
3. **Relationships** — How components connect
4. **Diagram recommendation** — Suggested layout for excalidraw skill

Example:

```
## Analysis Complete

This is a microservices e-commerce platform with 5 services, 2 databases,
and Redis caching. The API Gateway handles authentication and routes to
domain services.

### Ready for Diagram

Components identified: 12
Relationships mapped: 18
Recommended layout: Vertical flow (5 tiers)

Use the `excalidraw` skill to generate the architecture diagram.
```
