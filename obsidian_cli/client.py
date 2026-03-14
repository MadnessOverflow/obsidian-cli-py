import sys
import subprocess
import shutil
from typing import Optional, List, Dict, Any, Literal
from .exceptions import ObsidianCLINotFoundError, ObsidianCLICommandError, ObsidianCLIError

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
            command: The main obsidian command.
            *args: Additional positional arguments.
            **kwargs: Parameters and flags for the command.
        """
        is_windows = sys.platform == "win32"
        cmd_list: List[str] = [self.executable]

        if self.vault:
            if is_windows and ' ' in self.vault:
                cmd_list.append(f'vault="{self.vault}"')
            else:
                cmd_list.append(f"vault={self.vault}")

        cmd_list.append(command)
        cmd_list.extend(args)

        for k, v in kwargs.items():
            if k == "from_version":
                k = "from"  # Map 'from_version' safely to 'from'
            elif k == "to_version":
                k = "to"  # Map 'to_version' to 'to' 
            
            if v is True:
                cmd_list.append(str(k))
            elif v is False:
                continue
            elif v is not None:
                val_str = str(v)
                val_str = val_str.replace('\n', '\\n').replace('\t', '\\t')

                if is_windows and ' ' in val_str:
                    cmd_list.append(f'{k}="{val_str}"')
                else:
                    cmd_list.append(f"{k}={val_str}")

        cmd_string = " ".join(cmd_list)

        if is_windows:
            cmd_to_run = " ".join(cmd_list)
            use_shell = True
        else:
            cmd_to_run = cmd_list
            use_shell = False

        try:
            result = subprocess.run(
                cmd_to_run,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
                shell=use_shell
            )

            if result.stdout is None:
                raise ObsidianCLIError("Obsidian CLI returned no result")
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise ObsidianCLICommandError(
                command=" ".join(cmd_list),
                exit_code=e.returncode,
                stdout=e.stdout,
                stderr=e.stderr
            ) from e

    # ==========================================
    # General commands
    # ==========================================

    def help(self, command: Optional[str] = None) -> str:
        """
        Show list of all available commands.
        
        Args:
            command: Show help for a specific command.
        """
        if command:
            return self._run_command("help", command)
        return self._run_command("help")

    def version(self) -> str:
        """Show Obsidian version."""
        return self._run_command("version")

    def reload(self) -> str:
        """Reload the app window."""
        return self._run_command("reload")

    def restart(self) -> str:
        """Restart the app."""
        return self._run_command("restart")

    def execute(self, command: str, *args: str, **kwargs: Any) -> str:
        """
        Execute an arbitrary Obsidian CLI command, that is not implemented as a method of this class (f.ex. for third party plugins).
        
        Args:
            command: The command to execute (e.g., 'quickadd', 'quickadd:run').
            *args: Additional positional arguments.
            **kwargs: Command-specific parameters and flags.
        """
        return self._run_command(command, *args, **kwargs)

    # ==========================================
    # Bases
    # ==========================================

    def bases(self) -> str:
        """List all .base files in vault."""
        return self._run_command("bases")

    def base_views(self) -> str:
        """List views in the current base file."""
        return self._run_command("base:views")

    def base_create(self, file: Optional[str] = None, path: Optional[str] = None, view: Optional[str] = None,
                    name: Optional[str] = None, content: Optional[str] = None, 
                    open: bool = False, newtab: bool = False) -> str:
        """
        Create a new item in a base. Defaults to the active file if file/path omitted.
        
        Args:
            file: Base file name.
            path: Base file path.
            view: View name.
            name: New file name.
            content: Initial content.
            open: Open file after creating.
            newtab: Open in new tab.
        """
        return self._run_command("base:create", file=file, path=path, view=view, name=name, content=content, open=open, newtab=newtab)

    def base_query(self, file: Optional[str] = None, path: Optional[str] = None, view: Optional[str] = None,
                   format: Optional[Literal["json", "csv", "tsv", "md", "paths"]] = "json") -> str:
        """
        Query a base and return results.
        
        Args:
            file: Base file name.
            path: Base file path.
            view: View name to query.
            format: Output format (default: json).
        """
        return self._run_command("base:query", file=file, path=path, view=view, format=format)

    # ==========================================
    # Bookmarks
    # ==========================================

    def bookmarks(self, total: bool = False, verbose: bool = False, format: Optional[Literal["json", "tsv", "csv"]] = "tsv") -> str:
        """
        List bookmarks.
        
        Args:
            total: Return bookmark count.
            verbose: Include bookmark types.
            format: Output format (default: tsv).
        """
        return self._run_command("bookmarks", total=total, verbose=verbose, format=format)

    def bookmark(self, file: Optional[str] = None, subpath: Optional[str] = None, folder: Optional[str] = None,
                 search: Optional[str] = None, url: Optional[str] = None, title: Optional[str] = None) -> str:
        """
        Add a bookmark.
        
        Args:
            file: File to bookmark.
            subpath: Subpath (heading or block) within file.
            folder: Folder to bookmark.
            search: Search query to bookmark.
            url: URL to bookmark.
            title: Bookmark title.
        """
        return self._run_command("bookmark", file=file, subpath=subpath, folder=folder, search=search, url=url, title=title)

    # ==========================================
    # Command palette
    # ==========================================

    def commands(self, filter: Optional[str] = None) -> str:
        """
        List available command IDs.
        
        Args:
            filter: Filter by ID prefix.
        """
        return self._run_command("commands", filter=filter)

    def command(self, id: str) -> str:
        """
        Execute an Obsidian command.
        
        Args:
            id: Command ID to execute (required).
        """
        return self._run_command("command", id=id)

    def hotkeys(self, total: bool = False, verbose: bool = False, format: Optional[Literal["json", "tsv", "csv"]] = "tsv", all: bool = False) -> str:
        """
        List hotkeys.
        
        Args:
            total: Return hotkey count.
            verbose: Show if hotkey is custom.
            format: Output format (default: tsv).
            all: Include commands without hotkeys.
        """
        return self._run_command("hotkeys", total=total, verbose=verbose, format=format, all=all)

    def hotkey(self, id: str, verbose: bool = False) -> str:
        """
        Get hotkey for a command.
        
        Args:
            id: Command ID (required).
            verbose: Show if custom or default.
        """
        return self._run_command("hotkey", id=id, verbose=verbose)

    # ==========================================
    # Daily notes
    # ==========================================

    def daily(self, paneType: Optional[Literal["tab", "split", "window"]] = None) -> str:
        """
        Open daily note.
        
        Args:
            paneType: Pane type to open in.
        """
        return self._run_command("daily", paneType=paneType)

    def daily_path(self) -> str:
        """Get daily note path."""
        return self._run_command("daily:path")

    def daily_read(self) -> str:
        """Read daily note contents."""
        return self._run_command("daily:read")

    def daily_append(self, content: str, inline: bool = False, open: bool = False, paneType: Optional[Literal["tab", "split", "window"]] = None) -> str:
        """
        Append content to daily note.
        
        Args:
            content: Content to append (required).
            inline: Append without newline.
            open: Open file after adding.
            paneType: Pane type to open in.
        """
        return self._run_command("daily:append", content=content, inline=inline, open=open, paneType=paneType)

    def daily_prepend(self, content: str, inline: bool = False, open: bool = False, paneType: Optional[Literal["tab", "split", "window"]] = None) -> str:
        """
        Prepend content to daily note.
        
        Args:
            content: Content to prepend (required).
            inline: Prepend without newline.
            open: Open file after adding.
            paneType: Pane type to open in.
        """
        return self._run_command("daily:prepend", content=content, inline=inline, open=open, paneType=paneType)

    # ==========================================
    # File history
    # ==========================================

    def diff(self, file: Optional[str] = None, path: Optional[str] = None, 
             from_version: Optional[int] = None, to_version: Optional[int] = None, filter: Optional[Literal["local", "sync"]] = None) -> str:
        """
        List or diff local/sync versions. Defaults to the active file/path if omitted.
        
        Args:
            file: File name.
            path: File path.
            from_version: Version number to diff from. (aliased from 'from' to avoid Python keyword conflict)
            to_version: Version number to diff to. (aliased from 'to' for consistency)
            filter: Filter by version source.
        """
        return self._run_command("diff", file=file, path=path, from_version=from_version, to_version=to_version, filter=filter)

    def history(self, file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        List file history versions. Defaults to the active file/path if omitted.
        
        Args:
            file: File name.
            path: File path.
        """
        return self._run_command("history", file=file, path=path)

    def history_list(self) -> str:
        """List files with history."""
        return self._run_command("history:list")

    def history_read(self, file: Optional[str] = None, path: Optional[str] = None, version: int = 1) -> str:
        """
        Read a file history version. Defaults to the active file/path if omitted.
        
        Args:
            file: File name.
            path: File path.
            version: Version number (default: 1).
        """
        return self._run_command("history:read", file=file, path=path, version=version)

    def history_restore(self, version: int, file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Restore a file history version. Defaults to the active file/path if omitted.
        
        Args:
            version: Version number (required).
            file: File name.
            path: File path.
        """
        return self._run_command("history:restore", file=file, path=path, version=version)

    def history_open(self, file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Open file recovery. Defaults to the active file/path if omitted.
        
        Args:
            file: File name.
            path: File path.
        """
        return self._run_command("history:open", file=file, path=path)

    # ==========================================
    # Files and folders
    # ==========================================

    def file(self, file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Show file info. Defaults to the active file/path if omitted.
        
        Args:
            file: File name.
            path: File path.
        """
        return self._run_command("file", file=file, path=path)

    def files(self, folder: Optional[str] = None, ext: Optional[str] = None, total: bool = False) -> str:
        """
        List files in the vault.
        
        Args:
            folder: Filter by folder.
            ext: Filter by extension.
            total: Return file count.
        """
        return self._run_command("files", folder=folder, ext=ext, total=total)

    def folder(self, path: str, info: Optional[Literal["files", "folders", "size"]] = None) -> str:
        """
        Show folder info.
        
        Args:
            path: Folder path (required).
            info: Return specific info only.
        """
        return self._run_command("folder", path=path, info=info)

    def folders(self, folder: Optional[str] = None, total: bool = False) -> str:
        """
        List folders in the vault.
        
        Args:
            folder: Filter by parent folder.
            total: Return folder count.
        """
        return self._run_command("folders", folder=folder, total=total)

    def open(self, file: Optional[str] = None, path: Optional[str] = None, newtab: bool = False) -> str:
        """
        Open a file. Requires either file or path.
        
        Args:
            file: File name.
            path: File path.
            newtab: Open in new tab.
        """
        return self._run_command("open", file=file, path=path, newtab=newtab)

    def create(self, name: Optional[str] = None, path: Optional[str] = None, content: Optional[str] = None,
               template: Optional[str] = None, overwrite: bool = False, open: bool = False, newtab: bool = False) -> str:
        """
        Create a new file. When no name or path is provided creates "Unnamed.md" in root folder (like Ctrl+N).
        
        Args:
            name: File name.
            path: File path.
            content: Initial content.
            template: Template to use.
            overwrite: Overwrite if file exists.
            open: Open file after creating.
            newtab: Open in new tab.
        """
        return self._run_command("create", name=name, path=path, content=content, template=template, 
                                 overwrite=overwrite, open=open, newtab=newtab)

    def read(self, file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Read file contents. Defaults to the active file/path if omitted.
        
        Args:
            file: File name.
            path: File path.
        """
        return self._run_command("read", file=file, path=path)

    def append(self, content: str, file: Optional[str] = None, path: Optional[str] = None, inline: bool = False) -> str:
        """
        Append content to a file. Defaults to the active file if file/path is omitted.
        
        Args:
            content: Content to append (required).
            file: File name.
            path: File path.
            inline: Append without newline.
        """
        return self._run_command("append", content=content, file=file, path=path, inline=inline)

    def prepend(self, content: str, file: Optional[str] = None, path: Optional[str] = None, inline: bool = False) -> str:
        """
        Prepend content to a file. Defaults to the active file/path if omitted.
        
        Args:
            content: Content to prepend (required).
            file: File name.
            path: File path.
            inline: Prepend without newline.
        """
        return self._run_command("prepend", content=content, file=file, path=path, inline=inline)

    def move(self, to: str, file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Move or rename a file. Defaults to the active file/path if omitted.
        This will automatically update internal links if turned on in your vault settings.
        
        Args:
            to: Destination folder or path (required).
            file: File name.
            path: File path.
        """
        return self._run_command("move", file=file, path=path, to=to)

    def rename(self, name: str, file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Rename a file. Defaults to the active file/path if omitted.
        The file extension is preserved automatically if omitted from the new name. 
        Use move to rename and move a file at the same time. This will automatically update internal links if turned on in your vault settings.
        
        Args:
            name: New file name (required).
            file: File name.
            path: File path.
        """
        return self._run_command("rename", file=file, path=path, name=name)

    def delete(self, file: Optional[str] = None, path: Optional[str] = None, permanent: bool = False) -> str:
        """
        Delete a file. Defaults to the active file/path if omitted. Trash by default.
        
        Args:
            file: File name.
            path: File path.
            permanent: Skip trash, delete permanently.
        """
        return self._run_command("delete", file=file, path=path, permanent=permanent)

    # ==========================================
    # Links
    # ==========================================

    def backlinks(self, file: Optional[str] = None, path: Optional[str] = None, 
                  counts: bool = False, total: bool = False, format: Optional[Literal["json", "tsv", "csv"]] = "tsv") -> str:
        """
        List backlinks to a file. Defaults to the active file/path if omitted.
        
        Args:
            file: Target file name.
            path: Target file path.
            counts: Include link counts.
            total: Return backlink count.
            format: Output format (default: tsv).
        """
        return self._run_command("backlinks", file=file, path=path, counts=counts, total=total, format=format)

    def links(self, file: Optional[str] = None, path: Optional[str] = None, total: bool = False) -> str:
        """
        List outgoing links from a file. Defaults to the active file/path if omitted.
        
        Args:
            file: File name.
            path: File path.
            total: Return link count.
        """
        return self._run_command("links", file=file, path=path, total=total)

    def unresolved(self, total: bool = False, counts: bool = False, verbose: bool = False, format: Optional[Literal["json", "tsv", "csv"]] = "tsv") -> str:
        """
        List unresolved links in vault.
        
        Args:
            total: Return unresolved link count.
            counts: Include link counts.
            verbose: Include source files.
            format: Output format (default: tsv).
        """
        return self._run_command("unresolved", total=total, counts=counts, verbose=verbose, format=format)

    def orphans(self, total: bool = False, all: bool = False) -> str:
        """
        List files with no incoming links.
        
        Args:
            total: Return orphan count.
            all: Include non-markdown files.
        """
        return self._run_command("orphans", total=total, all=all)

    def deadends(self, total: bool = False, all: bool = False) -> str:
        """
        List files with no outgoing links.
        
        Args:
            total: Return dead-end count.
            all: Include non-markdown files.
        """
        return self._run_command("deadends", total=total, all=all)

    # ==========================================
    # Outline
    # ==========================================

    def outline(self, file: Optional[str] = None, path: Optional[str] = None, 
                format: Optional[Literal["tree", "md", "json"]] = "tree", total: bool = False) -> str:
        """
        Show headings for a file. Defaults to the active file/path if omitted.
        
        Args:
            file: File name.
            path: File path.
            format: Output format (default: tree).
            total: Return heading count.
        """
        return self._run_command("outline", file=file, path=path, format=format, total=total)

    # ==========================================
    # Plugins
    # ==========================================

    def plugins(self, filter: Optional[Literal["core", "community"]] = None, versions: bool = False, format: Optional[Literal["json", "tsv", "csv"]] = "tsv") -> str:
        """
        List installed plugins.
        
        Args:
            filter: Filter by plugin type.
            versions: Include version numbers.
            format: Output format (default: tsv).
        """
        return self._run_command("plugins", filter=filter, versions=versions, format=format)

    def plugins_enabled(self, filter: Optional[Literal["core", "community"]] = None, versions: bool = False, format: Optional[Literal["json", "tsv", "csv"]] = "tsv") -> str:
        """
        List enabled plugins.
        
        Args:
            filter: Filter by plugin type.
            versions: Include version numbers.
            format: Output format (default: tsv).
        """
        return self._run_command("plugins:enabled", filter=filter, versions=versions, format=format)

    def plugins_restrict(self, on: bool = False, off: bool = False) -> str:
        """
        Toggle or check restricted mode.
        
        Args:
            on: Enable restricted mode.
            off: Disable restricted mode.
        """
        return self._run_command("plugins:restrict", on=on, off=off)

    def plugin(self, id: str) -> str:
        """
        Get plugin info.
        
        Args:
            id: Plugin ID (required).
        """
        return self._run_command("plugin", id=id)

    def plugin_enable(self, id: str, filter: Optional[Literal["core", "community"]] = None) -> str:
        """
        Enable a plugin.
        
        Args:
            id: Plugin ID (required).
            filter: Plugin type.
        """
        return self._run_command("plugin:enable", id=id, filter=filter)

    def plugin_disable(self, id: str, filter: Optional[Literal["core", "community"]] = None) -> str:
        """
        Disable a plugin.
        
        Args:
            id: Plugin ID (required).
            filter: Plugin type.
        """
        return self._run_command("plugin:disable", id=id, filter=filter)

    def plugin_install(self, id: str, enable: bool = False) -> str:
        """
        Install a community plugin.
        
        Args:
            id: Plugin ID (required).
            enable: Enable after install.
        """
        return self._run_command("plugin:install", id=id, enable=enable)

    def plugin_uninstall(self, id: str) -> str:
        """
        Uninstall a community plugin.
        
        Args:
            id: Plugin ID (required).
        """
        return self._run_command("plugin:uninstall", id=id)

    def plugin_reload(self, id: str) -> str:
        """
        Reload a plugin (for developers).
        
        Args:
            id: Plugin ID (required).
        """
        return self._run_command("plugin:reload", id=id)

    # ==========================================
    # Properties
    # ==========================================

    def aliases(self, file: Optional[str] = None, path: Optional[str] = None, 
                total: bool = False, verbose: bool = False, active: bool = False) -> str:
        """
        List aliases in the vault. Use active or file/path to show aliases for a specific file.
        
        Args:
            file: File name.
            path: File path.
            total: Return alias count.
            verbose: Include file paths.
            active: Show aliases for active file.
        """
        return self._run_command("aliases", file=file, path=path, total=total, verbose=verbose, active=active)

    def properties(self, file: Optional[str] = None, path: Optional[str] = None, name: Optional[str] = None,
                   total: bool = False, sort: Optional[Literal["name", "count"]] = "name", counts: bool = False, 
                   format: Optional[Literal["yaml", "json", "tsv"]] = "yaml", active: bool = False) -> str:
        """
        List properties in the vault. 
        
        Args:
            file: Show properties for file.
            path: Show properties for path.
            name: Get specific property count.
            total: Return property count.
            sort: Specifies the sorting criterion. Sort by name or count (frequency) (default: name).
            counts: Include occurrence counts.
            format: Output format (default: yaml).
            active: Show properties for active file.
        """
        return self._run_command("properties", file=file, path=path, name=name, total=total, sort=sort, counts=counts, format=format, active=active)

    def property_set(self, name: str, value: str, type: Optional[Literal["text", "list", "number", "checkbox", "date", "datetime"]] = None, 
                     file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Set a property on a file. Defaults to the active file/path if omitted.
        
        Args:
            name: Property name (required).
            value: Property value (required).
            type: Property type.
            file: File name.
            path: File path.
        """
        return self._run_command("property:set", name=name, value=value, type=type, file=file, path=path)

    def property_remove(self, name: str, file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Remove a property from a file. Defaults to the active file/path if omitted.
        
        Args:
            name: Property name (required).
            file: File name.
            path: File path.
        """
        return self._run_command("property:remove", name=name, file=file, path=path)

    def property_read(self, name: str, file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Read a property value from a file. Defaults to the active file/path if omitted.
        
        Args:
            name: Property name (required).
            file: File name.
            path: File path.
        """
        return self._run_command("property:read", name=name, file=file, path=path)

    # ==========================================
    # Publish
    # ==========================================

    def publish_site(self) -> str:
        """Show publish site info (slug, URL)."""
        return self._run_command("publish:site")

    def publish_list(self, total: bool = False) -> str:
        """
        List published files.
        
        Args:
            total: Return published file count.
        """
        return self._run_command("publish:list", total=total)

    def publish_status(self, total: bool = False, new: bool = False, changed: bool = False, deleted: bool = False) -> str:
        """
        List publish changes.
        
        Args:
            total: Return change count.
            new: Show new files only.
            changed: Show changed files only.
            deleted: Show deleted files only.
        """
        return self._run_command("publish:status", total=total, new=new, changed=changed, deleted=deleted)

    def publish_add(self, file: Optional[str] = None, path: Optional[str] = None, changed: bool = False) -> str:
        """
        Publish a file or all changed files. Defaults to the active file/path if omitted.
        
        Args:
            file: File name.
            path: File path.
            changed: Publish all changed files.
        """
        return self._run_command("publish:add", file=file, path=path, changed=changed)

    def publish_remove(self, file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Unpublish a file. Defaults to the active file/path if omitted.
        
        Args:
            file: File name.
            path: File path.
        """
        return self._run_command("publish:remove", file=file, path=path)

    def publish_open(self, file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Open file on published site. Defaults to the active file/path if omitted.
        
        Args:
            file: File name.
            path: File path.
        """
        return self._run_command("publish:open", file=file, path=path)

    # ==========================================
    # Random notes
    # ==========================================

    def random(self, folder: Optional[str] = None, newtab: bool = False) -> str:
        """
        Open a random note.
        
        Args:
            folder: Limit to folder.
            newtab: Open in new tab.
        """
        return self._run_command("random", folder=folder, newtab=newtab)

    def random_read(self, folder: Optional[str] = None) -> str:
        """
        Read a random note.
        
        Args:
            folder: Limit to folder.
        """
        return self._run_command("random:read", folder=folder)

    # ==========================================
    # Search
    # ==========================================

    def search(self, query: str, path: Optional[str] = None, limit: Optional[int] = None, 
               total: bool = False, case: bool = False, format: Optional[Literal["text", "json"]] = "text") -> str:
        """
        Search vault for text. Returns matching file paths. 
        Case insensitive by default.
        
        Args:
            query: Search query (required).
            path: Limit to folder.
            limit: Max files.
            total: Return match count.
            case: Case sensitive.
            format: Output format (default: text).
        """
        return self._run_command("search", query=query, path=path, limit=limit, total=total, case=case, format=format)

    def search_context(self, query: str, path: Optional[str] = None, limit: Optional[int] = None, 
                       case: bool = False, format: Optional[Literal["text", "json"]] = "text") -> str:
        """
        Search with matching line context.
        Case insensitive by default. Returns grep-style path:line: text output.
        
        Args:
            query: Search query (required).
            path: Limit to folder.
            limit: Max files.
            case: Case sensitive.
            format: Output format (default: text).
        """
        return self._run_command("search:context", query=query, path=path, limit=limit, case=case, format=format)

    def search_open(self, query: Optional[str] = None) -> str:
        """
        Open search view.
        
        Args:
            query: Initial search query.
        """
        return self._run_command("search:open", query=query)

    # ==========================================
    # Sync
    # ==========================================

    def sync(self, on: bool = False, off: bool = False) -> str:
        """
        Pause or resume sync.
        
        Args:
            on: Resume sync.
            off: Pause sync.
        """
        return self._run_command("sync", on=on, off=off)

    def sync_status(self) -> str:
        """Show sync status."""
        return self._run_command("sync:status")

    def sync_history(self, file: Optional[str] = None, path: Optional[str] = None, total: bool = False) -> str:
        """
        List sync version history for a file. Defaults to the active file/path if omitted.
        
        Args:
            file: File name.
            path: File path.
            total: Return version count.
        """
        return self._run_command("sync:history", file=file, path=path, total=total)

    def sync_read(self, version: int, file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Read a sync version. Defaults to the active file/path if omitted.
        
        Args:
            version: Version number (required).
            file: File name.
            path: File path.
        """
        return self._run_command("sync:read", file=file, path=path, version=version)

    def sync_restore(self, version: int, file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Restore a sync version. Defaults to the active file/path if omitted.
        
        Args:
            version: Version number (required).
            file: File name.
            path: File path.
        """
        return self._run_command("sync:restore", file=file, path=path, version=version)

    def sync_open(self, file: Optional[str] = None, path: Optional[str] = None) -> str:
        """
        Open sync history. Defaults to the active file/path if omitted.
        
        Args:
            file: File name.
            path: File path.
        """
        return self._run_command("sync:open", file=file, path=path)

    def sync_deleted(self, total: bool = False) -> str:
        """
        List deleted files in sync.
        
        Args:
            total: Return deleted file count.
        """
        return self._run_command("sync:deleted", total=total)

    # ==========================================
    # Tags
    # ==========================================

    def tags(self, file: Optional[str] = None, path: Optional[str] = None, total: bool = False, 
             counts: bool = False, sort: Optional[str] = None, format: Optional[Literal["json", "tsv", "csv"]] = None, 
             active: bool = False) -> str:
        """
        List tags in the vault. Use active or file/path to show tags for a specific file.
        
        Args:
            file: File name.
            path: File path.
            total: Return tag count.
            counts: Include tag counts.
            sort: Sort by count (default: name).
            format: Output format (default: tsv).
            active: Show tags for active file.
        """
        return self._run_command("tags", file=file, path=path, total=total, counts=counts, sort=sort, format=format, active=active)

    def tag(self, name: str, total: bool = False, verbose: bool = False) -> str:
        """
        Get tag info.
        
        Args:
            name: Tag name (required).
            total: Return occurrence count.
            verbose: Include file list and count.
        """
        return self._run_command("tag", name=name, total=total, verbose=verbose)

    # ==========================================
    # Tasks
    # ==========================================

    def tasks(self, file: Optional[str] = None, path: Optional[str] = None, total: bool = False,
              done: bool = False, todo: bool = False, status: Optional[str] = None, verbose: bool = False,
              format: Optional[Literal["text", "json", "tsv", "csv"]] = "text", active: bool = False, daily: bool = False) -> str:
        """
        List tasks in the vault. Use active or file/path to show tasks for a specific file.
        
        Args:
            file: Filter by file name.
            path: Filter by file path.
            total: Return task count.
            done: Show completed tasks.
            todo: Show incomplete tasks.
            status: Filter by status character. (status character = char inside of brackets, e.g. [x] -> status = x)
            verbose: Group by file with line numbers.
            format: Output format (default: text).
            active: Show tasks for active file.
            daily: Show tasks from daily note.
        """
        return self._run_command("tasks", file=file, path=path, total=total, done=done, todo=todo, status=status, verbose=verbose, format=format, active=active, daily=daily)

    def task(self, ref: Optional[str] = None, file: Optional[str] = None, path: Optional[str] = None,
             line: Optional[int] = None, toggle: bool = False, done: bool = False, todo: bool = False,
             daily: bool = False, status: Optional[str] = None) -> str:
        """
        Show or update a task.
        
        Args:
            ref: Task reference (path:line).
            file: File name.
            path: File path.
            line: Line number.
            toggle: Toggle task status.
            done: Mark as done.
            todo: Mark as todo.
            daily: Use daily note.
            status: Set status character. (status character = char inside of brackets, e.g. [x] -> status = x)
        """
        return self._run_command("task", ref=ref, file=file, path=path, line=line, toggle=toggle, done=done, todo=todo, daily=daily, status=status)

    # ==========================================
    # Templates
    # ==========================================

    def templates(self, total: bool = False) -> str:
        """
        List templates.
        
        Args:
            total: Return template count.
        """
        return self._run_command("templates", total=total)

    def template_read(self, name: str, resolve: bool = False, title: Optional[str] = None) -> str:
        """
        Read template content.
        
        Args:
            name: Template name (required).
            resolve: Resolve template variables. (resolve option processes {{date}}, {{time}}, {{title}} variables)
            title: Title for variable resolution.
        """
        return self._run_command("template:read", name=name, resolve=resolve, title=title)

    def template_insert(self, name: str) -> str:
        """
        Insert template into active file.
        
        Args:
            name: Template name (required).
        """
        return self._run_command("template:insert", name=name)

    # ==========================================
    # Themes and snippets
    # ==========================================

    def themes(self, versions: bool = False) -> str:
        """
        List installed themes.
        
        Args:
            versions: Include version numbers.
        """
        return self._run_command("themes", versions=versions)

    def theme(self, name: Optional[str] = None) -> str:
        """
        Show active theme or get info.
        
        Args:
            name: Theme name for details.
        """
        return self._run_command("theme", name=name)

    def theme_set(self, name: str) -> str:
        """
        Set active theme.
        
        Args:
            name: Theme name (empty for default) (required).
        """
        return self._run_command("theme:set", name=name)

    def theme_install(self, name: str, enable: bool = False) -> str:
        """
        Install a community theme.
        
        Args:
            name: Theme name (required).
            enable: Activate after install.
        """
        return self._run_command("theme:install", name=name, enable=enable)

    def theme_uninstall(self, name: str) -> str:
        """
        Uninstall a theme.
        
        Args:
            name: Theme name (required).
        """
        return self._run_command("theme:uninstall", name=name)

    def snippets(self) -> str:
        """List installed CSS snippets."""
        return self._run_command("snippets")

    def snippets_enabled(self) -> str:
        """List enabled CSS snippets."""
        return self._run_command("snippets:enabled")

    def snippet_enable(self, name: str) -> str:
        """
        Enable a CSS snippet.
        
        Args:
            name: Snippet name (required).
        """
        return self._run_command("snippet:enable", name=name)

    def snippet_disable(self, name: str) -> str:
        """
        Disable a CSS snippet.
        
        Args:
            name: Snippet name (required).
        """
        return self._run_command("snippet:disable", name=name)

    # ==========================================
    # Unique notes
    # ==========================================

    def unique(self, name: Optional[str] = None, content: Optional[str] = None, 
               paneType: Optional[Literal["tab", "split", "window"]] = None, open: bool = False) -> str:
        """
        Create unique note.
        
        Args:
            name: Note name.
            content: Initial content.
            paneType: Pane type to open in.
            open: Open file after creating.
        """
        return self._run_command("unique", name=name, content=content, paneType=paneType, open=open)

    # ==========================================
    # Vault
    # ==========================================

    def vault_info(self, info: Optional[Literal["name", "path", "files", "folders", "size"]] = None) -> str:
        """
        Show vault info.
        
        Args:
            info: Return specific info only.
        """
        return self._run_command("vault", info=info)

    def vaults(self, total: bool = False, verbose: bool = False) -> str:
        """
        List known vaults.
        
        Args:
            total: Return vault count.
            verbose: Include vault paths.
        """
        return self._run_command("vaults", total=total, verbose=verbose)

    # NOTE: vault:open wasn't requested

    # ==========================================
    # Web viewer
    # ==========================================

    def web(self, url: str, newtab: bool = False) -> str:
        """
        Open URL in web viewer.
        
        Args:
            url: URL to open (required).
            newtab: Open in new tab.
        """
        return self._run_command("web", url=url, newtab=newtab)

    # ==========================================
    # Wordcount
    # ==========================================

    def wordcount(self, file: Optional[str] = None, path: Optional[str] = None, words: bool = False, characters: bool = False) -> str:
        """
        Count words and characters. Defaults to the active file/path if omitted
        
        Args:
            file: File name.
            path: File path.
            words: Return word count only.
            characters: Return character count only.
        """
        return self._run_command("wordcount", file=file, path=path, words=words, characters=characters)

    # ==========================================
    # Workspace
    # ==========================================

    def workspace(self, ids: bool = False) -> str:
        """
        Show workspace tree.
        
        Args:
            ids: Include workspace item IDs.
        """
        return self._run_command("workspace", ids=ids)

    def workspaces(self, total: bool = False) -> str:
        """
        List saved workspaces.
        
        Args:
            total: Return workspace count.
        """
        return self._run_command("workspaces", total=total)

    def workspace_save(self, name: Optional[str] = None) -> str:
        """
        Save current layout as workspace.
        
        Args:
            name: Workspace name.
        """
        return self._run_command("workspace:save", name=name)

    def workspace_load(self, name: str) -> str:
        """
        Load a saved workspace.
        
        Args:
            name: Workspace name (required).
        """
        return self._run_command("workspace:load", name=name)

    def workspace_delete(self, name: str) -> str:
        """
        Delete a saved workspace.
        
        Args:
            name: Workspace name (required).
        """
        return self._run_command("workspace:delete", name=name)

    def tabs(self, ids: bool = False) -> str:
        """
        List open tabs.
        
        Args:
            ids: Include tab IDs.
        """
        return self._run_command("tabs", ids=ids)

    def tab_open(self, group: Optional[str] = None, file: Optional[str] = None, view: Optional[str] = None) -> str:
        """
        Open a new tab.
        
        Args:
            group: Tab group ID.
            file: File to open.
            view: View type to open.
        """
        return self._run_command("tab:open", group=group, file=file, view=view)

    def recents(self, total: bool = False) -> str:
        """
        List recently opened files.
        
        Args:
            total: Return recent file count.
        """
        return self._run_command("recents", total=total)
