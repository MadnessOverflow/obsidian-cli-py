import pytest
import subprocess
from obsidian_cli import ObsidianClient, ObsidianCLINotFoundError, ObsidianCLICommandError


@pytest.fixture
def mock_shutil_which(mocker):
    # Mock shutil.which to pretend obsidian is installed
    return mocker.patch('obsidian_cli.client.shutil.which', return_value='/usr/local/bin/obsidian')


@pytest.fixture
def mock_subprocess_run(mocker):
    mock = mocker.patch('obsidian_cli.client.subprocess.run')
    # Default successful mock return
    mock.return_value.returncode = 0
    mock.return_value.stdout = "Success output\n"
    mock.return_value.stderr = ""
    return mock


def test_init_executable_not_found(mocker):
    mocker.patch('obsidian_cli.client.shutil.which', return_value=None)
    with pytest.raises(ObsidianCLINotFoundError):
        ObsidianClient()


def test_init_success(mock_shutil_which):
    client = ObsidianClient(vault="My Vault")
    assert client.vault == "My Vault"
    assert client.executable == "obsidian"


def test_run_command_basic(mock_shutil_which, mock_subprocess_run):
    client = ObsidianClient()
    result = client._run_command("help")
    
    assert result == "Success output"
    mock_subprocess_run.assert_called_once_with(
        ['obsidian', 'help'],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True
    )


def test_run_command_vault_and_flags(mock_shutil_which, mock_subprocess_run):
    client = ObsidianClient(vault="Test")
    client._run_command("create", name="Note", content="Hello", open=True, overwrite=False, dummy_val=123)

    mock_subprocess_run.assert_called_once_with(
        ['obsidian', 'vault=Test', 'create', 'name=Note', 'content=Hello', 'open', 'dummy_val=123'],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True
    )


def test_run_command_failure(mock_shutil_which, mock_subprocess_run):
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=['obsidian', 'search'],
        output="Command failed stderr"
    )

    client = ObsidianClient()
    with pytest.raises(ObsidianCLICommandError) as exc_info:
        client.search("query")
    
    assert exc_info.value.exit_code == 1
    assert "Command 'obsidian search query=query format=text' failed" in str(exc_info.value)
