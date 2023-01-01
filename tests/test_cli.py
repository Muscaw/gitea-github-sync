import textwrap
from typing import List
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from gitea_github_sync.cli import cli
from gitea_github_sync.repository import Repository, Visibility


@pytest.fixture
def repositories_fixture() -> List[Repository]:
    return [
        Repository("some-team/a-repo", Visibility.PUBLIC),
        Repository("some-team/b-repo", Visibility.PRIVATE),
        Repository("some-team/c-repo", Visibility.UNKNOWN),
    ]


@patch("gitea_github_sync.cli.github.get_github", autospec=True)
@patch("gitea_github_sync.cli.github.list_all_repositories", autospec=True)
def test_list_all_repositories(
    mock_list_all_repositories: MagicMock,
    mock_get_github: MagicMock,
    repositories_fixture: List[Repository],
) -> None:
    mock_github = MagicMock()
    mock_get_github.return_value = mock_github
    mock_list_all_repositories.return_value = repositories_fixture

    runner = CliRunner()
    result = runner.invoke(cli, ["list-all-repositories"])

    assert result.output == "some-team/a-repo\nsome-team/b-repo\nsome-team/c-repo\n"
    assert result.exit_code == 0


@patch("gitea_github_sync.cli.github.get_github", autospec=True)
@patch("gitea_github_sync.cli.github.list_all_repositories", autospec=True)
def test_list_all_repositories_with_stats(
    mock_list_all_repositories: MagicMock,
    mock_get_github: MagicMock,
    repositories_fixture: List[Repository],
) -> None:
    mock_github = MagicMock()
    mock_get_github.return_value = mock_github
    mock_list_all_repositories.return_value = repositories_fixture

    runner = CliRunner()
    result = runner.invoke(cli, ["list-all-repositories", "--stats"])

    expected_result = textwrap.dedent(
        """\
    some-team/a-repo
    some-team/b-repo
    some-team/c-repo

    Repository stats
    Number of public repos identified: 1
    Number of private repos identified: 1
    Number of unknown repos identified: 1
    Total number of repos identified: 3
    """
    )

    assert result.output == expected_result
    assert result.exit_code == 0
