class ObsidianCLIError(Exception):
    """Base class for all exceptions raised by py-obsidian-cli-wrapper."""
    pass


class ObsidianCLINotFoundError(ObsidianCLIError):
    """Raised when the 'obsidian' executable cannot be found in the system PATH."""
    pass


class ObsidianCLICommandError(ObsidianCLIError):
    """Raised when an obsidian CLI command fails (non-zero exit code)."""
    def __init__(self, command: str, exit_code: int, stdout: str, stderr: str):
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        message = f"Command '{command}' failed with exit status {exit_code}.\nStdout: {stdout}\nStderr: {stderr}"
        super().__init__(message)
