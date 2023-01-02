from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
from piny import ValidationError

from gitea_github_sync.config import Config, config_file_location, load_config

VALID_CONFIG_FILE = """
github_token: some-github-token
gitea_api_url: https://some-gitea-url.com
gitea_token: some-gitea-token
"""

VALID_CONFIG = Config(
    github_token="some-github-token",
    gitea_api_url="https://some-gitea-url.com",
    gitea_token="some-gitea-token",
)

DEFAULT_CONFIG_FILE_PATH = config_file_location()


@patch("builtins.open", new_callable=mock_open, read_data=VALID_CONFIG_FILE)
def test_load_config(mock_file_open: MagicMock) -> None:
    config = load_config()

    assert config == VALID_CONFIG
    mock_file_open.assert_called_once_with(DEFAULT_CONFIG_FILE_PATH)


@patch("builtins.open", new_callable=mock_open, read_data=VALID_CONFIG_FILE)
def test_load_config_non_default_path(mock_file_open: MagicMock) -> None:
    other_path = Path("/config.yml")
    config = load_config(config_location=other_path)

    assert config == VALID_CONFIG
    mock_file_open.assert_called_once_with(other_path)


@patch("builtins.open", new_callable=mock_open, read_data="bad-file")
def test_load_config_bad_file(mock_file_open: MagicMock) -> None:
    with pytest.raises(ValidationError):
        load_config()

    mock_file_open.assert_called_once_with(DEFAULT_CONFIG_FILE_PATH)
