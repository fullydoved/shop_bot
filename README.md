# Beavs - Shop Bot

Your friendly Canadian shop assistant for Maple Leaf Makers.

Beavs helps you manage your workshop inventory, track projects, and stay on task.

## Features

- **Inventory Management**: Track items across Akro-Mills storage bins using natural language
- **Project Tracking**: Create and manage maker projects
- **Task Management**: Keep track of what needs to be done
- **Multiple Interfaces**: CLI, Web Dashboard, and (coming soon) Voice

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose
- Ollama running on your host machine with a model pulled (e.g., `ollama pull llama3.2`)

### Deployment

```bash
# Clone the repo
git clone git@github.com:fullydoved/shop_bot.git
cd shop_bot

# Start Beavs
docker compose up -d

# Visit http://localhost:42069
```

### First-time Setup

Create an admin user:
```bash
docker compose exec beavs python manage.py createsuperuser
```

## Local Development

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Navigate to Django project
cd shop_bot

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### CLI Mode

Talk to Beavs directly from your terminal:

```bash
python manage.py beavs
```

## Usage Examples

### Adding Inventory

```
You: Bin A3 has M3 screws, M4 nuts, and some JST connectors
Beavs: Added 3 item(s) to bin A3: M3 screws, M4 nuts, JST connectors
```

### Finding Items

```
You: Where are my M3 screws?
Beavs: Found 1 item(s):
- M3 screws in bin A3
```

### Managing Projects

```
You: Start a new project for the robot arm
Beavs: Created project: robot arm

You: Add a task to order more servos
Beavs: Created task: order more servos (priority: medium)
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Model to use for chat |
| `DATA_DIR` | `./data` | Directory for SQLite database |

## Project Structure

```
shop_bot/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── shop_bot/               # Django project
│   ├── inventory/          # Inventory models & services
│   ├── projects/           # Project & task management
│   ├── assistant/          # AI/Ollama integration
│   ├── dashboard/          # Web interface
│   ├── cli/                # CLI interface
│   └── templates/          # HTML templates
└── data/                   # Persistent data (SQLite)
```

## Contributing

Made with love for Maple Leaf Makers.
