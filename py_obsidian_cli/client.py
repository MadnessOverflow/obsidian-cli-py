import subprocess
import shutil
from typing import Optional, List, Dict, Any
from .exceptions import ObsidianCLINotFoundError, ObsidianCLICommandError

class ObsidianClient:
    """A client for interacting with the Obsidian CLI."""

    def __init__(self, vault: Optional[str] = None, executable: str = "obsidian"):
        """
        Initialize the ObsidianClient.

        Args:
            vault: The name or ID of the vault to target (optional).
            executable: The path to the obsidian executable (default: 'obsidian').
        """
        self.vault = vault
        self.executable = executable
        self._check_executable()

    def _check_executable(self) -> None:
        """Check if the obsidian executable is available in PATH."""
        if shutil.which(self.executable) is None:
            raise ObsidianCLINotFoundError(
                f"The executable '{self.executable}' was not found in PATH. "
                "Ensure Obsidian is installed and the CLI is enabled."
            )

    def _run_command(self, command: str, *args: str, **kwargs: Any) -> str:
        """
        Run an obsidian CLI command.

        Args:
            command: The main obsidian command (e.g., 'create', 'search').
            *args: Any additional positional arguments.
            **kwargs: Parameters and flags for the command.

        Returns:
            The standard output (stdout) of the command as a string.

        Raises:
            ObsidianCLICommandError: If the command returns a non-zero exit status.
        """
        cmd_list: List[str] = [self.executable]

        if self.vault:
            cmd_list.append(f"vault={self.vault}")

        cmd_list.append(command)
        cmd_list.extend(args)

        for k, v in kwargs.items():
            if v is True:
                cmd_list.append(str(k))
            elif v is False:
                continue
            elif v is not None:
                val_str = str(v)
                cmd_list.append(f"{k}={val_str}")

        try:
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise ObsidianCLICommandError(
                command=" ".join(cmd_list),
                exit_code=e.returncode,
                stdout=e.stdout,
                stderr=e.stderr
            ) from e

    # ==========================================
    # File Management Commands
    # ==========================================

    def create(self, name: Optional[str] = None, content: Optional[str] = None, open: bool = False, overwrite: bool = False, **kwargs: Any) -> str:
        """
        Create a new note.
        
        Args:
            name: The name or path of the new note.
            content: The text content of the new note.
            open: If True, opens the note in Obsidian after creation.
            overwrite: If True, overwrites an existing note with the same name.
            **kwargs: Extra parameters/flags mapped to the CLI.
        """
        return self._run_command("create", name=name, content=content, open=open, overwrite=overwrite, **kwargs)

    def read(self, file: Optional[str] = None, path: Optional[str] = None, **kwargs: Any) -> str:
        """
        Read the content of a note.
        
        Args:
            file: The name of the file to read (resolved via Obsidian's wikilink resolution).
            path: The exact path from the vault root to read.
        """
        return self._run_command("read", file=file, path=path, **kwargs)

    def append(self, file: Optional[str] = None, path: Optional[str] = None, content: Optional[str] = None, **kwargs: Any) -> str:
        """Append content to a note."""
        return self._run_command("append", file=file, path=path, content=content, **kwargs)

    def prepend(self, file: Optional[str] = None, path: Optional[str] = None, content: Optional[str] = None, **kwargs: Any) -> str:
        """Prepend content to a note."""
        return self._run_command("prepend", file=file, path=path, content=content, **kwargs)

    def move(self, source: str, destination: str, **kwargs: Any) -> str:
        """Move or rename a file (if arguments are purely positional to the CLI)."""
        # Note: Obsidian CLI might use parameters for this, but if positional, we use `*args`
        # Adjusting assuming parameter style based on previous docs if needed, but going with 
        # kwargs to allow overriding if the CLI args vary.
        return self._run_command("move", source, destination, **kwargs)

    def rename(self, source: str, destination: str, **kwargs: Any) -> str:
        """Rename a file."""
        return self._run_command("rename", source, destination, **kwargs)

    def delete(self, file: Optional[str] = None, path: Optional[str] = None, **kwargs: Any) -> str:
        """Delete a file."""
        return self._run_command("delete", file=file, path=path, **kwargs)

    def open(self, file: Optional[str] = None, path: Optional[str] = None, **kwargs: Any) -> str:
        """Open a file in Obsidian."""
        return self._run_command("open", file=file, path=path, **kwargs)

    # ==========================================
    # Search Commands
    # ==========================================

    def search(self, query: str, **kwargs: Any) -> str:
        """
        Search the vault.
        
        Args:
            query: The search query.
        """
        return self._run_command("search", query=query, **kwargs)

    # ==========================================
    # Daily Notes Commands
    # ==========================================

    def daily(self, **kwargs: Any) -> str:
        """Open today's daily note, creating it if it doesn't exist."""
        return self._run_command("daily", **kwargs)

    def daily_read(self, **kwargs: Any) -> str:
        """Read today's daily note."""
        return self._run_command("daily:read", **kwargs)

    def daily_append(self, content: str, **kwargs: Any) -> str:
        """Append content to today's daily note."""
        return self._run_command("daily:append", content=content, **kwargs)

    def daily_prepend(self, content: str, **kwargs: Any) -> str:
        """Prepend content to today's daily note."""
        return self._run_command("daily:prepend", content=content, **kwargs)

    # ==========================================
    # Properties Commands
    # ==========================================

    def properties(self, file: Optional[str] = None, path: Optional[str] = None, **kwargs: Any) -> str:
        """List properties of a note."""
        return self._run_command("properties", file=file, path=path, **kwargs)

    def property_set(self, key: str, value: str, file: Optional[str] = None, path: Optional[str] = None, **kwargs: Any) -> str:
        """Set a property on a note."""
        # Typically set like: obsidian property:set key=myKey value=myValue file=Note
        return self._run_command("property:set", key=key, value=value, file=file, path=path, **kwargs)

    def property_read(self, key: str, file: Optional[str] = None, path: Optional[str] = None, **kwargs: Any) -> str:
        """Read a property from a note."""
        return self._run_command("property:read", key=key, file=file, path=path, **kwargs)
        
    def property_remove(self, key: str, file: Optional[str] = None, path: Optional[str] = None, **kwargs: Any) -> str:
        """Remove a property from a note."""
        return self._run_command("property:remove", key=key, file=file, path=path, **kwargs)

    # ==========================================
    # Bookmarks
    # ==========================================

    def bookmarks(self, **kwargs: Any) -> str:
        """List all bookmarks."""
        return self._run_command("bookmarks", **kwargs)

    def bookmark(self, **kwargs: Any) -> str:
        """Manage a bookmark (see CLI help for specific usage)."""
        return self._run_command("bookmark", **kwargs)

    # ==========================================
    # Tags
    # ==========================================

    def tags(self, **kwargs: Any) -> str:
        """List all tags."""
        return self._run_command("tags", **kwargs)

    def tag(self, name: str, **kwargs: Any) -> str:
        """Interact with a specific tag."""
        return self._run_command("tag", name=name, **kwargs)

    # ==========================================
    # Workspaces
    # ==========================================

    def workspace_save(self, name: str, **kwargs: Any) -> str:
        """Save the current workspace."""
        return self._run_command("workspace:save", name=name, **kwargs)

    def workspace_load(self, name: str, **kwargs: Any) -> str:
        """Load a saved workspace."""
        return self._run_command("workspace:load", name=name, **kwargs)

    def tabs(self, **kwargs: Any) -> str:
        """List open tabs."""
        return self._run_command("tabs", **kwargs)

    # ==========================================
    # System & Other
    # ==========================================

    def help(self, **kwargs: Any) -> str:
        """Show CLI help."""
        return self._run_command("help", **kwargs)
        
    def version(self, **kwargs: Any) -> str:
        """Show CLI version."""
        return self._run_command("version", **kwargs)

    def commands(self, **kwargs: Any) -> str:
        """Show all available Obsidian commands."""
        return self._run_command("commands", **kwargs)

    def command(self, id: str, **kwargs: Any) -> str:
        """Run a specific Obsidian command by ID."""
        return self._run_command("command", id=id, **kwargs)
