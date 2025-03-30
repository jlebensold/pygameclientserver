# Pygame Client-Server Game

A multiplayer game built with Python and Pygame that demonstrates client-server architecture.

## Prerequisites

- Python 3.8 or higher
- `uv` package manager (for faster dependency installation)
- Poetry (for dependency management)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pygameclientserver
```

2. Set up the virtual environment and install dependencies:
```bash
# Create virtual environment and install poetry
uv venv
source .venv/bin/activate
uv pip install poetry

# Install project dependencies
poetry install
```

## Running the Game

The game consists of a server and multiple clients. The `run_game.sh` script automates the process of starting and stopping all components.

### Using the Run Script

1. Make sure the run script is executable:
```bash
chmod +x run_game.sh
```

2. Run the game:
```bash
./run_game.sh
```

This script will:
- Start the game server
- Launch 2 client instances
- Wait for you to press Enter to stop all instances

### Manual Control

If you prefer to run components manually:

1. Start the server:
```bash
poetry run python server.py
```

2. In separate terminals, start clients:
```bash
poetry run python client.py
```

## Stopping the Game

- If using the run script: Simply press Enter in the terminal where the script is running
- If running manually: Use Ctrl+C in each terminal window

## Project Structure

- `server.py`: The game server that manages game state and client connections
- `client.py`: The game client that handles user input and displays the game
- `run_game.sh`: Shell script to automate starting and stopping the game
- `pyproject.toml`: Project configuration and dependency management
- `requirements.txt`: Basic dependency list (for reference)

## Development

The project uses Poetry for dependency management. To add new dependencies:

```bash
poetry add package-name
```

## License

This project is licensed under the terms specified in the LICENSE file. 