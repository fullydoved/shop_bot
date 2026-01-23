# BEAVS - Bin Entry And Verification System

A Canadian-themed shop assistant for maker spaces, powered by Claude AI.

## Overview

BEAVS (aka "Beavs") is a shop inventory and project management system with a natural language interface. It uses the Claude API for understanding commands and managing inventory, projects, and tasks through conversation.

**Personality:** Friendly Canadian hoser - says "eh" and "bud", keeps responses brief.

## Features

- **Inventory Management** - Track items in bins with categories, quantities, units
- **Project Management** - Create and track projects with statuses (idea/active/paused/completed)
- **Task Management** - Tasks with priorities, notes, optional project linking
- **Natural Language Chat** - Talk to Beavs to manage everything
- **Web Interface** - Dashboard, inventory, projects, and tasks pages

## Architecture

```
shop_bot/
├── assistant/           # Claude AI integration
│   ├── claude_client.py # API wrapper
│   ├── processor.py     # Input processing & history management
│   ├── prompts.py       # System prompt & tool definitions
│   └── commands.py      # Tool execution handlers
├── dashboard/           # Main dashboard & chat
├── inventory/           # Inventory models, views, services
└── projects/            # Projects & tasks models, views, services
```

## Chat Tools

### Inventory
| Tool | Description | Example |
|------|-------------|---------|
| `add_inventory_items` | Add items to a bin | "Bin A1 has 50 M3 screws" |
| `find_inventory` | Search for items | "Where are my screws?" |

### Projects
| Tool | Description | Example |
|------|-------------|---------|
| `create_project` | Create a project | "Start a drone build project" |
| `list_projects` | List all projects | "Show my projects" |
| `update_project` | Update status/name | "Mark drone build as active" |
| `delete_project` | Delete a project | "Delete the LED lamp project" |

### Tasks
| Tool | Description | Example |
|------|-------------|---------|
| `create_task` | Create task (standalone or linked) | "Add task to Trident: lube rails" |
| `get_pending_tasks` | List pending tasks | "What's on my list?" |
| `list_tasks` | List all tasks | "Show completed tasks" |
| `complete_task` | Mark task done | "Mark order PLA as done" |
| `update_task` | Update task details | "Add note to lube rails: waiting on parts" |
| `delete_task` | Delete a task | "Delete the clean bench task" |

## Claude API Setup

### 1. Get API Key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Navigate to **API Keys** → **Create Key**
3. Copy the key (starts with `sk-ant-...`)

### 2. Configure Environment
```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-your-key-here
CLAUDE_MODEL=claude-sonnet-4-5-20250929
```

### 3. Restart
```bash
docker compose restart
```

## Cost Management

### Current Settings (optimized)
- **max_tokens:** 300 (short, punchy responses)
- **History limit:** 10 messages (prevents token bloat)
- **System prompt:** ~80 tokens (minimal)

### Estimated Costs (Sonnet 4.5)
| Scenario | Cost/Interaction | Monthly (50/day) |
|----------|-----------------|------------------|
| Optimized | ~$0.01-0.02 | ~$15-30 |
| With Haiku | ~$0.005 | ~$7.50 |

### Available Models
| Model | ID | Cost (In/Out per MTok) |
|-------|-----|------------------------|
| Haiku 4.5 | `claude-haiku-4-5-20251001` | $1 / $5 |
| Sonnet 4 | `claude-sonnet-4-20250514` | $3 / $15 |
| Opus 4 | `claude-opus-4-20250514` | $15 / $75 |

## Web Pages

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | Stats, chat with Beavs, pending tasks |
| Inventory | `/inventory/` | All items, inline editing, add/delete |
| Projects | `/projects/` | Project list, click for details |
| Project Detail | `/projects/<id>/` | Project tasks, add tasks |
| Tasks | `/tasks/` | All tasks, filter by project/status |

## Development

### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Key Files to Edit
- `assistant/prompts.py` - Personality, tool definitions
- `assistant/commands.py` - Tool execution logic
- `*/services.py` - Business logic
- `templates/` - UI templates

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "ANTHROPIC_API_KEY not set" | Check `.env`, restart container |
| High costs | Switch to Haiku, check history limit |
| Beavs too chatty | Reduce max_tokens in `claude_client.py` |
| Tool not working | Check `commands.py` handler, `prompts.py` definition |

## Resources

- [Claude API Docs](https://docs.anthropic.com/)
- [Anthropic Console](https://console.anthropic.com)
- [Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
