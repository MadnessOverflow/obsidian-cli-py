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

    # ==========================================
    # Aliases, Links, and Outline
    # ==========================================

    def aliases(self, **kwargs: Any) -> str:
        """List aliases in the vault."""
        return self._run_command("aliases", **kwargs)

    def backlinks(self, **kwargs: Any) -> str:
        """List backlinks to a file."""
        return self._run_command("backlinks", **kwargs)

    def deadends(self, **kwargs: Any) -> str:
        """List files with no outgoing links."""
        return self._run_command("deadends", **kwargs)

    def links(self, **kwargs: Any) -> str:
        """List outgoing links from a file."""
        return self._run_command("links", **kwargs)

    def orphans(self, **kwargs: Any) -> str:
        """List files with no incoming links."""
        return self._run_command("orphans", **kwargs)

    def outline(self, **kwargs: Any) -> str:
        """Show headings for the current file."""
        return self._run_command("outline", **kwargs)

    def unresolved(self, **kwargs: Any) -> str:
        """List unresolved links in vault."""
        return self._run_command("unresolved", **kwargs)

    # ==========================================
    # Bases
    # ==========================================

    def base_create(self, **kwargs: Any) -> str:
        """Create a new item in a base."""
        return self._run_command("base:create", **kwargs)

    def base_query(self, **kwargs: Any) -> str:
        """Query a base and return results."""
        return self._run_command("base:query", **kwargs)

    def base_views(self, **kwargs: Any) -> str:
        """List views in the current base file."""
        return self._run_command("base:views", **kwargs)

    def bases(self, **kwargs: Any) -> str:
        """List all base files in vault."""
        return self._run_command("bases", **kwargs)

    # ==========================================
    # Daily Notes and Random Notes
    # ==========================================

    def daily_path(self, **kwargs: Any) -> str:
        """Get daily note path."""
        return self._run_command("daily:path", **kwargs)

    def random(self, **kwargs: Any) -> str:
        """Open a random note."""
        return self._run_command("random", **kwargs)

    def random_read(self, **kwargs: Any) -> str:
        """Read a random note."""
        return self._run_command("random:read", **kwargs)

    # ==========================================
    # Files, Folders, and History
    # ==========================================

    def file_info(self, **kwargs: Any) -> str:
        """Show file info."""
        return self._run_command("file", **kwargs)

    def files(self, **kwargs: Any) -> str:
        """List files in the vault."""
        return self._run_command("files", **kwargs)

    def folder(self, **kwargs: Any) -> str:
        """Show folder info."""
        return self._run_command("folder", **kwargs)

    def folders(self, **kwargs: Any) -> str:
        """List folders in the vault."""
        return self._run_command("folders", **kwargs)

    def history(self, **kwargs: Any) -> str:
        """List file history versions."""
        return self._run_command("history", **kwargs)

    def history_list(self, **kwargs: Any) -> str:
        """List files with history."""
        return self._run_command("history:list", **kwargs)

    def history_open(self, **kwargs: Any) -> str:
        """Open file recovery."""
        return self._run_command("history:open", **kwargs)

    def history_read(self, **kwargs: Any) -> str:
        """Read a file history version."""
        return self._run_command("history:read", **kwargs)

    def history_restore(self, **kwargs: Any) -> str:
        """Restore a file history version."""
        return self._run_command("history:restore", **kwargs)

    def diff(self, **kwargs: Any) -> str:
        """List or diff local/sync versions."""
        return self._run_command("diff", **kwargs)

    def recents(self, **kwargs: Any) -> str:
        """List recently opened files."""
        return self._run_command("recents", **kwargs)

    # ==========================================
    # Plugins, Themes, and Snippets
    # ==========================================

    def plugin(self, **kwargs: Any) -> str:
        """Get plugin info."""
        return self._run_command("plugin", **kwargs)

    def plugin_disable(self, **kwargs: Any) -> str:
        """Disable a plugin."""
        return self._run_command("plugin:disable", **kwargs)

    def plugin_enable(self, **kwargs: Any) -> str:
        """Enable a plugin."""
        return self._run_command("plugin:enable", **kwargs)

    def plugin_install(self, **kwargs: Any) -> str:
        """Install a community plugin."""
        return self._run_command("plugin:install", **kwargs)

    def plugin_reload(self, **kwargs: Any) -> str:
        """Reload a plugin."""
        return self._run_command("plugin:reload", **kwargs)

    def plugin_uninstall(self, **kwargs: Any) -> str:
        """Uninstall a community plugin."""
        return self._run_command("plugin:uninstall", **kwargs)

    def plugins(self, **kwargs: Any) -> str:
        """List installed plugins."""
        return self._run_command("plugins", **kwargs)

    def plugins_enabled(self, **kwargs: Any) -> str:
        """List enabled plugins."""
        return self._run_command("plugins:enabled", **kwargs)

    def plugins_restrict(self, **kwargs: Any) -> str:
        """Toggle or check restricted mode."""
        return self._run_command("plugins:restrict", **kwargs)

    def theme(self, **kwargs: Any) -> str:
        """Show active theme or get info."""
        return self._run_command("theme", **kwargs)

    def theme_install(self, **kwargs: Any) -> str:
        """Install a community theme."""
        return self._run_command("theme:install", **kwargs)

    def theme_set(self, **kwargs: Any) -> str:
        """Set active theme."""
        return self._run_command("theme:set", **kwargs)

    def theme_uninstall(self, **kwargs: Any) -> str:
        """Uninstall a theme."""
        return self._run_command("theme:uninstall", **kwargs)

    def themes(self, **kwargs: Any) -> str:
        """List installed themes."""
        return self._run_command("themes", **kwargs)

    def snippet_disable(self, **kwargs: Any) -> str:
        """Disable a CSS snippet."""
        return self._run_command("snippet:disable", **kwargs)

    def snippet_enable(self, **kwargs: Any) -> str:
        """Enable a CSS snippet."""
        return self._run_command("snippet:enable", **kwargs)

    def snippets(self, **kwargs: Any) -> str:
        """List installed CSS snippets."""
        return self._run_command("snippets", **kwargs)

    def snippets_enabled(self, **kwargs: Any) -> str:
        """List enabled CSS snippets."""
        return self._run_command("snippets:enabled", **kwargs)

    # ==========================================
    # Publish and Unique Notes
    # ==========================================

    def publish_site(self, **kwargs: Any) -> str:
        """Show publish site info (slug, URL)."""
        return self._run_command("publish:site", **kwargs)

    def publish_list(self, **kwargs: Any) -> str:
        """List published files."""
        return self._run_command("publish:list", **kwargs)

    def publish_status(self, **kwargs: Any) -> str:
        """List publish changes."""
        return self._run_command("publish:status", **kwargs)

    def publish_add(self, **kwargs: Any) -> str:
        """Publish a file or all changed files."""
        return self._run_command("publish:add", **kwargs)

    def publish_remove(self, **kwargs: Any) -> str:
        """Unpublish a file."""
        return self._run_command("publish:remove", **kwargs)

    def publish_open(self, **kwargs: Any) -> str:
        """Open file on published site."""
        return self._run_command("publish:open", **kwargs)

    def unique(self, **kwargs: Any) -> str:
        """Create unique note."""
        return self._run_command("unique", **kwargs)

    # ==========================================
    # Tasks and Templates
    # ==========================================

    def task(self, **kwargs: Any) -> str:
        """Show or update a task."""
        return self._run_command("task", **kwargs)

    def tasks(self, **kwargs: Any) -> str:
        """List tasks in the vault."""
        return self._run_command("tasks", **kwargs)

    def template_insert(self, **kwargs: Any) -> str:
        """Insert template into active file."""
        return self._run_command("template:insert", **kwargs)

    def template_read(self, **kwargs: Any) -> str:
        """Read template content."""
        return self._run_command("template:read", **kwargs)

    def templates(self, **kwargs: Any) -> str:
        """List templates."""
        return self._run_command("templates", **kwargs)

    # ==========================================
    # Search Extensions
    # ==========================================

    def search_context(self, **kwargs: Any) -> str:
        """Search with matching line context."""
        return self._run_command("search:context", **kwargs)

    def search_open(self, **kwargs: Any) -> str:
        """Open search view."""
        return self._run_command("search:open", **kwargs)

    # ==========================================
    # Sync
    # ==========================================

    def sync(self, **kwargs: Any) -> str:
        """Pause or resume sync."""
        return self._run_command("sync", **kwargs)

    def sync_deleted(self, **kwargs: Any) -> str:
        """List deleted files in sync."""
        return self._run_command("sync:deleted", **kwargs)

    def sync_history(self, **kwargs: Any) -> str:
        """List sync version history for a file."""
        return self._run_command("sync:history", **kwargs)

    def sync_open(self, **kwargs: Any) -> str:
        """Open sync history."""
        return self._run_command("sync:open", **kwargs)

    def sync_read(self, **kwargs: Any) -> str:
        """Read a sync version."""
        return self._run_command("sync:read", **kwargs)

    def sync_restore(self, **kwargs: Any) -> str:
        """Restore a sync version."""
        return self._run_command("sync:restore", **kwargs)

    def sync_status(self, **kwargs: Any) -> str:
        """Show sync status."""
        return self._run_command("sync:status", **kwargs)

    # ==========================================
    # Vault, Workspace Extensions, System
    # ==========================================

    def vault_info(self, **kwargs: Any) -> str:
        """Show vault info (renamed from vault to not conflict with self.vault parameter)."""
        return self._run_command("vault", **kwargs)

    def vaults(self, **kwargs: Any) -> str:
        """List known vaults."""
        return self._run_command("vaults", **kwargs)

    def workspace_info(self, **kwargs: Any) -> str:
        """Show workspace tree."""
        return self._run_command("workspace", **kwargs)

    def workspace_delete(self, **kwargs: Any) -> str:
        """Delete a saved workspace."""
        return self._run_command("workspace:delete", **kwargs)

    def workspaces(self, **kwargs: Any) -> str:
        """List saved workspaces."""
        return self._run_command("workspaces", **kwargs)

    def tab_open(self, **kwargs: Any) -> str:
        """Open a new tab."""
        return self._run_command("tab:open", **kwargs)

    def hotkey(self, **kwargs: Any) -> str:
        """Get hotkey for a command."""
        return self._run_command("hotkey", **kwargs)

    def hotkeys(self, **kwargs: Any) -> str:
        """List hotkeys."""
        return self._run_command("hotkeys", **kwargs)

    def reload(self, **kwargs: Any) -> str:
        """Reload the vault."""
        return self._run_command("reload", **kwargs)

    def restart(self, **kwargs: Any) -> str:
        """Restart the app."""
        return self._run_command("restart", **kwargs)

    def web(self, **kwargs: Any) -> str:
        """Open URL in web viewer."""
        return self._run_command("web", **kwargs)

    def wordcount(self, **kwargs: Any) -> str:
        """Count words and characters."""
        return self._run_command("wordcount", **kwargs)

