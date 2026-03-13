"""
py-obsidian-cli-wrapper

A Python wrapper for the Obsidian CLI.
"""

from .client import ObsidianClient
from .exceptions import ObsidianCLIError, ObsidianCLINotFoundError, ObsidianCLICommandError

__version__ = "0.1.0"
__all__ = [
    "ObsidianClient",
    "ObsidianCLIError",
    "ObsidianCLINotFoundError",
    "ObsidianCLICommandError",
]
