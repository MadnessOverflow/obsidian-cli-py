# py-obsidian-cli-wrapper

**py-obsidian-cli-wrapper** is an unofficial, easy-to-use Python bridge for the new [Obsidian CLI](https://help.obsidian.md/cli).

It allows you to programmatically interact with your Obsidian vaults, create notes, search your knowledge base, and much more, straight from Python!

## Features

- 🚀 **Simple and Intuitive API**: Pythonic wrappers around `obsidian` terminal commands.
- 📦 **Zero Dependencies**: Uses standard Python `subprocess` to communicate with the CLI.
- 🗂 **Multi-Vault Support**: Easily target specific vaults.
- 📝 **Fully Typed**: Includes type hints for an excellent IDE experience (autocomplete, type checking).

## Installation

*(Coming soon to PyPI)*
```bash
pip install py-obsidian-cli-wrapper
```

> **Note**: This library requires the official [Obsidian CLI](https://help.obsidian.md/cli) to be installed and enabled in your Obsidian app (requires Obsidian v1.11.7+ or early access 1.12.x+). The Obsidian app must be running for the CLI to work.

## Quick Start

```python
from py_obsidian_cli import ObsidianClient

# Initialize the client. Optionally specify a vault name.
client = ObsidianClient(vault="My Vault")

# Create a new note and open it in Obsidian
client.create(name="My First programmatic note", content="# Hello World\n\nThis was created via Python!", open=True, overwrite=True)

# Read the contents of a note
content = client.read(file="My First programmatic note")
print(content)

# Search your vault
results = client.search(query="Python")
print(results)
```

## Available Commands

The wrapper aims to support all major Obsidian CLI commands:

- **File Management**: `create`, `read`, `append`, `prepend`, `move`, `rename`, `delete`
- **Search**: `search`
- **Daily Notes**: `daily`, `daily:read`, `daily:append`
- **Properties**: `properties`, `property:set`, `property:read`
- *And many more...*

## How it works

The Python library translates your method calls into the corresponding terminal CLI syntax. For example:

```python
client.create(name="Note", content="Hello", open=True)
```
Translates to the shell command:
```bash
obsidian vault="My Vault" create name="Note" content="Hello" open
```

## Contributing

Contributions are welcome! If a command is missing, feel free to submit a Pull Request.

1. Clone the repository.
2. Run `poetry install` (or your preferred environment manager).
3. Run tests with `pytest`.
