# BEAVS - Bin Entry And Verification System

A shop assistant for maker spaces, powered by Claude AI with voice, lighting, and music control.

## Overview

BEAVS (aka "Beavs") is a shop inventory and project management system with a natural language interface. It uses the Claude API for understanding commands and managing inventory, projects, tasks, lighting, and music through conversation.

**Personality:** Helpful and casual, keeps it brief. Gets straight to the point.

## Features

- **Inventory Management** - Track items in bins with categories, quantities, positions
- **Project & Task Management** - Projects with statuses, tasks with priorities and project linking
- **Tool Checkout** - Track who borrowed what tool and when
- **Timed Reminders** - "Remind me in 20 minutes to flip the part"
- **Weather** - Current conditions, spray painting suitability check
- **Text-to-Speech** - Beavs talks back using Piper TTS (local, offline)
- **Speech-to-Text** - Push-to-talk voice input using faster-whisper (local, offline)
- **WLED Lighting Control** - 8 zones (4 walls + 4 corners), colors, effects, KITT-style audio sync
- **Chromecast Music** - Play/pause/skip, volume control, now playing status
- **Web Dashboard** - Chat interface, inventory, projects, tasks pages
- **CLI Interface** - `python manage.py beavs` for terminal REPL

## Architecture

```
shop_bot/
├── assistant/           # Claude AI integration
│   ├── claude_client.py # API wrapper
│   ├── processor.py     # Input processing & history management
│   ├── prompts.py       # System prompt & tool definitions (37 tools)
│   ├── commands.py      # Tool execution handlers
│   ├── tts.py           # Piper TTS integration
│   └── stt.py           # Whisper STT integration
├── dashboard/           # Web UI & chat
├── inventory/           # Bins, items, audit logging
├── projects/            # Projects & tasks
├── lighting/            # WLED control (8 segments)
├── chromecast/          # Music playback control
├── reminders/           # Timed reminders with APScheduler
├── tools/               # Tool checkout system
└── cli/                 # Terminal REPL interface
```

## Chat Tools (37 total)

### Inventory (6 tools)
| Tool | Description | Example |
|------|-------------|---------|
| `add_inventory_items` | Add/update items in a bin | "Bin A1 has 50 M3 screws on the left" |
| `find_inventory` | Search for items | "Where are my screws?" |
| `use_inventory_item` | Remove quantity from item | "Use 5 M3 screws" |
| `delete_inventory_item` | Delete an item | "Delete the M3 screws" |
| `get_inventory_log` | View recent activity | "Show inventory log" |
| `clear_inventory` | Delete ALL items | "Clear all inventory" |

**Fastener Name Normalization:** When adding fasteners, names are auto-normalized:
| Input | Stored As |
|-------|-----------|
| `socket head cap screw M3x6mm` | `SHCS M3x6mm` |
| `m3 button head 10` | `BHCS M3x10mm` |
| `flat head M4x8` | `FHCS M4x8mm` |
| `grub screw M4x5` | `GRUB M4x5mm` |
| `M5 hex nut` | `HEX NUT M5` |
| `washer M4` | `WASHER M4` |

**Query Expansion:** Searching expands natural terms to abbreviations:
- `screws` finds SHCS, BHCS, FHCS, GRUB items
- `socket head` finds SHCS items
- `nuts` finds HEX NUT items
- `washers` finds WASHER items

### Bins (3 tools)
| Tool | Description | Example |
|------|-------------|---------|
| `find_empty_bins` | Find available bins | "What bins are empty?" |
| `delete_bin` | Delete empty bin | "Delete bin A1" |
| `cleanup_empty_bins` | Delete all empty bins | "Clean up empty bins" |

### Projects (4 tools)
| Tool | Description | Example |
|------|-------------|---------|
| `create_project` | Create a project | "Start a drone build project" |
| `list_projects` | List all projects | "Show my projects" |
| `update_project` | Update status/name | "Mark drone build as active" |
| `delete_project` | Delete a project | "Delete the LED lamp project" |

### Tasks (6 tools)
| Tool | Description | Example |
|------|-------------|---------|
| `create_task` | Create task (standalone or linked) | "Add task to Trident: lube rails" |
| `get_pending_tasks` | List pending tasks | "What's on my list?" |
| `list_tasks` | List tasks (filter by status/project) | "What's on the Trident project?" |
| `complete_task` | Mark task done | "Mark order PLA as done" |
| `update_task` | Update task details | "Add note to lube rails: waiting on parts" |
| `delete_task` | Delete a task | "Delete the clean bench task" |

### Lighting (4 tools)
| Tool | Description | Example |
|------|-------------|---------|
| `control_lights` | On/off, brightness | "Turn on the shop lights" |
| `set_light_color` | Set zone color | "Make the north wall red" |
| `set_light_effect` | Set lighting effect | "Set rainbow effect on all" |
| `get_light_status` | Current light state | "What are the lights doing?" |

**Zones:** `all`, `walls`, `corners`, `north`/`n`, `south`/`s`, `east`/`e`, `west`/`w`, `ne`, `nw`, `se`, `sw`
**Colors:** red, green, blue, white, warm, cool, orange, purple, yellow, pink, cyan, magenta, or hex (#FF0000)
**Effects:** solid, blink, breathe, wipe, random, rainbow, scan, fade, chase, fire, twinkle, fireworks

### Music (3 tools)
| Tool | Description | Example |
|------|-------------|---------|
| `control_music` | Play/pause/skip/stop | "Pause the music" |
| `set_music_volume` | Set or adjust volume | "Turn it up" / "Volume 50" |
| `get_music_status` | Now playing info | "What's playing?" |

### Weather (1 tool)
| Tool | Description | Example |
|------|-------------|---------|
| `get_weather` | Current conditions, painting check | "What's the weather?" / "Good day for painting?" |

### Reminders (4 tools)
| Tool | Description | Example |
|------|-------------|---------|
| `set_reminder` | Set a timed reminder | "Remind me in 20 min to flip the part" |
| `list_reminders` | Show pending/triggered reminders | "What reminders do I have?" |
| `cancel_reminder` | Cancel a pending reminder | "Cancel the glue reminder" |
| `dismiss_reminder` | Acknowledge a triggered reminder | "Dismiss that reminder" |

**Time formats:** `30s`, `5 minutes`, `1h`, `1h30m`, `2 hours 15 minutes`

### Tool Checkout (6 tools)
| Tool | Description | Example |
|------|-------------|---------|
| `add_shop_tool` | Add a tool to the system | "Add the drill press to tools" |
| `checkout_tool` | Borrow a tool | "I'm taking the angle grinder" |
| `return_tool` | Return a borrowed tool | "Returning the drill press" |
| `find_shop_tool` | Find tool / who has it | "Where's my multimeter?" |
| `list_shop_tools` | List all tools & status | "What tools are checked out?" |
| `remove_shop_tool` | Remove tool from system | "Remove the broken drill" |

## Text-to-Speech

Beavs speaks responses using **Piper TTS** (offline, runs locally):
- Voice model: `en_US-ryan-high` (downloaded at Docker build)
- Toggle on dashboard with speaker icon
- **KITT-style lights:** When enabled, WLED brightness modulates with speech audio
- Adjustable light sync delay slider (-200ms to +200ms)

## Speech-to-Text

Push-to-talk voice input using **faster-whisper** (offline, runs locally):
- Model: `base` (~150MB, downloaded at Docker build)
- Hold the 🎤 button, speak, release to transcribe
- Transcribed text auto-submits to chat
- Requires ffmpeg (installed in container)

## Docker Setup

```bash
# Build and run
docker compose up -d

# View logs
docker compose logs -f

# Restart after .env changes
docker compose restart
```

**Container details:**
- Single container, no external dependencies (Redis, etc.)
- Network mode: host (for mDNS/Chromecast discovery)
- Data persisted to `./data:/app/data` (SQLite DB)
- Port: 42069

## Configuration (.env)

```bash
# Required
DJANGO_SECRET_KEY=your-secret-key       # Generate: python -c "import secrets; print(secrets.token_urlsafe(50))"
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional
CLAUDE_MODEL=claude-haiku-4-5-20251001  # Default model
WLED_HOST=http://192.168.1.23           # WLED controller IP
CHROMECAST_IP=192.168.1.50              # Direct IP (optional, uses mDNS otherwise)
OPENWEATHER_API_KEY=your-api-key        # OpenWeatherMap API key (free tier)
WEATHER_LOCATION=Toronto,CA              # Default location for weather
```

## Cost Management

- **max_tokens:** 300 (short responses)
- **History limit:** 10 messages

| Model | ID | Cost (In/Out per MTok) |
|-------|-----|------------------------|
| Haiku 4.5 | `claude-haiku-4-5-20251001` | $1 / $5 |
| Sonnet 4 | `claude-sonnet-4-20250514` | $3 / $15 |
| Opus 4 | `claude-opus-4-20250514` | $15 / $75 |

## Web Pages

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | Chat, stats, pending tasks, TTS toggle |
| Inventory | `/inventory/` | Items, inline edit, add/delete |
| Projects | `/projects/` | Project list with status |
| Project Detail | `/projects/<id>/` | Project tasks |
| Tasks | `/tasks/` | All tasks, filter by project/status |
| TTS | `/tts/?text=hello` | Direct TTS endpoint (WAV audio) |
| STT | `/stt/` | POST audio file, returns JSON `{text: "..."}` |

## CLI Interface

```bash
# Inside container
python manage.py beavs

# Commands
/help   - Show help
/clear  - Clear history
/quit   - Exit
```

## Development

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Key files
assistant/prompts.py   # System prompt, tool definitions
assistant/commands.py  # Tool execution handlers
assistant/tts.py       # Piper TTS
assistant/stt.py       # Whisper STT
lighting/services.py   # WLED API
chromecast/services.py # Chromecast control
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key error | Check `.env`, restart container |
| TTS not working | Check libsndfile1 installed, voice model downloaded |
| STT not working | Check ffmpeg installed, microphone permissions in browser |
| Lights not responding | Verify WLED_HOST in `.env`, check WLED is reachable |
| Chromecast not found | Set CHROMECAST_IP directly, or check mDNS/network |
| High API costs | Switch to Haiku model |

## Resources

- [Claude API Docs](https://docs.anthropic.com/)
- [Piper TTS](https://github.com/rhasspy/piper)
- [WLED](https://kno.wled.ge/)
- [Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
