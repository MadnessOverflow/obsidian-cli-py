# obsidian-cli-py

[![PyPI version](https://img.shields.io/pypi/v/obsidian-cli-py.svg)](https://pypi.org/project/obsidian-cli-py/)
[![Obsidian CLI Docs](https://img.shields.io/badge/docs-Obsidian_CLI-blue.svg)](https://help.obsidian.md/cli)

**obsidian-cli-py** is an unofficial, easy-to-use Python bridge for the new [Obsidian CLI](https://help.obsidian.md/cli).

It allows you to programmatically interact with your Obsidian vaults, create notes, search your knowledge base, and much more, straight from Python!

## Features

- 🚀 **Simple and Intuitive API**: Pythonic wrappers around `obsidian` terminal commands.
- 📦 **Lightweight**: Uses standard Python `subprocess` to communicate with the CLI.
- 📝 **Fully Typed**: Includes type hints for an excellent IDE experience (autocomplete, type checking).
- 📖 **In-Editor Documentation**: The official Obsidian CLI documentation has been integrated directly into the docstrings. You'll see all function explanations right in your IDE without needing to open the browser!

## Installation

```bash
pip install obsidian-cli-py
```

> **Note**: This library requires the official [Obsidian CLI](https://help.obsidian.md/cli) to be installed and enabled in your Obsidian app (requires Obsidian v1.12.4+). Check the official docs for troubleshooting and setup instructions.

## Documentation

Currently, this library does not maintain its own separate web documentation. 

Because **every function in this library corresponds 1:1 to the official CLI commands**, you can simply rely on the [official Obsidian CLI documentation](https://help.obsidian.md/cli). Operations like `obsidian search` become `client.search()`, `obsidian base:create` becomes `client.base_create()`, and so on.

## Quick Start

```python
from obsidian_cli import ObsidianClient

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

The wrapper aims to support all Obsidian CLI commands except developer commands.

### Additional Commands

- **Run arbitrary/plugin commands**: You can run commands registered by third-party plugins (like QuickAdd) using the generic execution method:
  ```python
  client.execute(command="quickadd", choice="My Choice")
  ```

## How it works

The Python library simply translates your method calls into the corresponding terminal CLI syntax. Pretty self-explanatory 🐐.

For example:

```python
client.create(name="Note", content="Hello", open=True)
```
Translates to the shell command:
```bash
obsidian vault="My Vault" create name="Note" content="Hello" open
```

## Contributing

Contributions are welcome! If a command is missing or something needs fixing, feel free to submit a Pull Request.

1. Clone the repository.
2. Run `poetry install` (or your preferred environment manager).
3. Run tests with `pytest`.
