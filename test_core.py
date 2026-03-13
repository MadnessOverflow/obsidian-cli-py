import sys
from py_obsidian_cli import ObsidianClient, ObsidianCLINotFoundError

def main():
    try:
        # Note: 'obsidian-dummy' forces the not found error for testing purposes,
        # unless you actually have obsidian in your PATH, then we could use 'obsidian'.
        client = ObsidianClient(executable="obsidian-dummy")
        print("Client initialized successfully.")
    except ObsidianCLINotFoundError as e:
        print(f"Expected error caught: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
