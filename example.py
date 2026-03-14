import sys
from obsidian_cli import ObsidianClient, ObsidianCLINotFoundError

def main():
    try:
        client = ObsidianClient(vault="Second Brain", executable="obsidian")
        print("Client initialized successfully.")
        print(client.help())
    except ObsidianCLINotFoundError as e:
        print(f"Expected error caught: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
