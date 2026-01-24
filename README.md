# B.E.A.V.S. - Bin Entry And Verification System

Your friendly Canadian shop assistant for the maker space.

Beavs helps you manage workshop inventory, track projects, control lighting, and play music - all through natural language chat.

## Features

- **Inventory Management**: Track items across storage bins with quantities, categories, and positions
- **Inventory Audit Log**: Full history of all inventory changes (add, update, delete, move)
- **Bin Management**: Find empty bins, clean up unused bins
- **Project Tracking**: Create and manage maker projects
- **Task Management**: Standalone tasks or linked to projects
- **WLED Lighting Control**: Control shop lights by zone (walls, corners, individual)
- **Chromecast Music**: Play/pause, skip, volume control for shop speaker
- **Web Dashboard**: HTMX-powered responsive UI
- **Chat Interface**: Natural language interaction powered by Claude

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Anthropic API key ([console.anthropic.com](https://console.anthropic.com))
- Optional: WLED controllers for lighting
- Optional: Chromecast device for music

### Setup

```bash
# Clone the repo
git clone git@github.com:fullydoved/shop_bot.git
cd shop_bot

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Start Beavs
docker compose up -d

# Run migrations (first time only)
docker compose exec beavs python manage.py migrate

# Visit http://localhost:42069
```

## Configuration

Create a `.env` file from the example:

```bash
# Required
DJANGO_SECRET_KEY=generate-with-python   # python -c "import secrets; print(secrets.token_urlsafe(50))"
ANTHROPIC_API_KEY=sk-ant-your-key-here
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# Optional: WLED lighting (comma-separated host:name pairs)
# WLED_DEVICES=192.168.1.100:north,192.168.1.101:south

# Optional: Chromecast
# CHROMECAST_NAME=Shop Speaker
```

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | - | **Required** - Django secret key |
| `ANTHROPIC_API_KEY` | - | **Required** - Claude API key |
| `CLAUDE_MODEL` | `claude-sonnet-4-5-20250929` | Claude model to use |
| `WLED_DEVICES` | - | WLED controllers (host:name,...) |
| `CHROMECAST_NAME` | - | Chromecast device name |
| `DATA_DIR` | `/app/data` | SQLite database location |

## Usage Examples

### Inventory

```
You: Add 50 M3x8mm bolts to bin A1
Beavs: Added M3x8mm bolts to bin A1, eh!

You: Where are the M3 bolts?
Beavs: Found in bin A1 - 50 pcs

You: Used 5 M3 bolts
Beavs: Used 5 M3x8mm bolts. 45 remaining in bin A1.

You: Show inventory log
Beavs: [Shows full audit history]

You: Find empty bins
Beavs: Empty bins available: B2, C1, C3
```

### Projects & Tasks

```
You: Start a new project called Drone Build
Beavs: Created project: Drone Build (idea)

You: Add task to Drone Build: order flight controller
Beavs: Created task: order flight controller for Drone Build

You: What tasks are pending?
Beavs: [Lists all pending tasks]
```

### Lighting

```
You: Turn on the shop lights
Beavs: All lights on, bud!

You: Set north wall to blue
Beavs: North wall set to blue.

You: Dim the corners to 50%
Beavs: Corners dimmed to 50%.
```

### Music

```
You: What's playing?
Beavs: [Shows current track info]

You: Skip this song
Beavs: Skipped to next track, eh!

You: Volume up
Beavs: Volume increased to 60%.
```

## Project Structure

```
shop_bot/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── shop_bot/
    ├── inventory/      # Inventory models, services, audit log
    ├── projects/       # Project & task management
    ├── assistant/      # Claude integration, chat tools
    ├── dashboard/      # Web interface
    ├── lighting/       # WLED integration
    ├── chromecast/     # Music control
    └── templates/      # HTMX templates
```

## Development

```bash
# Local setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd shop_bot
python manage.py migrate
python manage.py runserver

# Run tests
pytest

# Lint
ruff check .
```

## API Tools

Beavs exposes these chat tools:

| Tool | Description |
|------|-------------|
| `add_inventory_items` | Add items to a bin |
| `find_inventory` | Search for items |
| `use_inventory_item` | Remove quantity from item |
| `delete_inventory_item` | Delete an item |
| `get_inventory_log` | View audit history |
| `find_empty_bins` | List available bins |
| `delete_bin` | Remove empty bin |
| `cleanup_empty_bins` | Remove all empty bins |
| `create_project` | Start a new project |
| `list_projects` | View all projects |
| `create_task` | Add a task |
| `list_tasks` | View tasks |
| `complete_task` | Mark task done |
| `control_lights` | On/off/brightness |
| `set_light_color` | Change light color |
| `set_light_effect` | Set lighting effect |
| `control_music` | Play/pause/skip |
| `set_music_volume` | Adjust volume |

## License

Made with love for the maker community.
