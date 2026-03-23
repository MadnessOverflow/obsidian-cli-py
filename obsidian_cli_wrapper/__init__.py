"""
wrapper-for-obsidian-cli

An unofficial, easy-to-use python bridge/wrapper for the new Obsidian CLI.
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
