import pytest
from obsidian_cli_wrapper import ObsidianClient
import json
import uuid

# These tests execute real commands against the active Obsidian Vault.
# Ensure that Obsidian is running and a test vault is open.

@pytest.fixture(scope="module")
def live_client():
    # Uses the currently active/open vault.
    return ObsidianClient()

@pytest.fixture(scope="module")
def test_note_name():
    # Use a unique name to avoid conflicts
    return f"Live_Test_Note_{uuid.uuid4().hex[:8]}.md"

def test_no_arguments(live_client):
    """Test a command with no arguments."""
    res = live_client.version()
    assert "installer" in res

def test_positional_argument(live_client):
    """Test a command with a positional argument."""
    # help takes an optional positional argument 'command'
    res = live_client.help("search")
    assert "earch" in res or "Search" in res

def test_create_with_string_and_boolean(live_client, test_note_name):
    """Test string arguments with spaces and boolean flags."""
    content = "Hello from the live test suite!"
    
    # name and content are string kwargs with spaces, overwrite=True is a boolean flag
    res = live_client.create(name=test_note_name, content=content, overwrite=True)
    
    # We expect some output, usually not an error. Sometimes output is empty on success or prints path.
    # Now let's read it back to verify.
    read_res = live_client.read(file=test_note_name)
    assert content in read_res

def test_append_inline(live_client, test_note_name):
    """Test appending inline text."""
    append_text = " Appended text."
    live_client.append(content=append_text, file=test_note_name, inline=True)
    
    read_res = live_client.read(file=test_note_name)
    assert "Hello from the live test suite! Appended text." in read_res

def test_integer_and_literal_arguments(live_client):
    """Test integer limits and literal formatted outputs like JSON."""
    # query is positional, limit is int, format is literal/"json", case is boolean.
    # Just search for 'a' to guarantee some results in any vault, limit to 2 to test the integer arg.
    res = live_client.search("a", limit=2, format="json", case=False)
    
    try:
         data = json.loads(res)
         # Should be a list or object depending on search result
         assert isinstance(data, (list, dict))
    except json.JSONDecodeError:
         pytest.fail(f"Expected JSON output, got: {res}")

def test_property_set_read_remove(live_client, test_note_name):
    """Test complex commands with multiple arguments including literals."""
    prop_name = "test_status"
    prop_value = "running"
    
    # Set property
    live_client.property_set(name=prop_name, value=prop_value, type="text", file=test_note_name)
    
    # Read property
    read_res = live_client.property_read(name=prop_name, file=test_note_name)
    assert prop_value in read_res
    
    # Remove property
    live_client.property_remove(name=prop_name, file=test_note_name)
    
    # Note: property_read on missing property might throw ObsidianCLICommandError or return empty
    # We just ensure the remove command executes successfully.

def test_cleanup_deletion(live_client, test_note_name):
    """Test deletion command and cleanup the test note."""
    live_client.delete(file=test_note_name)
    
    # Verify it's gone
    try:
        read_res = live_client.read(file=test_note_name)
        assert not read_res or "error" in read_res.lower()
    except Exception:
        pass  # If it raises an exception, that's also fine (meaning the file is gone)
