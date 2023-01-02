import textwrap
from io import StringIO
from typing import List
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from gitea_github_sync.cli import cli, print_repositories
from gitea_github_sync.repository import Repository, Visibility


@pytest.fixture
def repositories_fixture() -> List[Repository]:
    return [
        Repository("some-team/a-repo", Visibility.PUBLIC),
        Repository("some-team/b-repo", Visibility.PRIVATE),
        Repository("some-team/c-repo", Visibility.UNKNOWN),
    ]


@pytest.mark.parametrize("expected_stat", [True, False])
@patch("gitea_github_sync.cli.print_repositories", autospec=True)
@patch("gitea_github_sync.cli.github.get_github", autospec=True)
@patch("gitea_github_sync.cli.github.list_all_repositories", autospec=True)
def test_list_all_github_repositories(
    mock_list_all_repositories: MagicMock,
    mock_get_github: MagicMock,
    mock_print_repositories: MagicMock,
    expected_stat: bool,
    repositories_fixture: List[Repository],
) -> None:
    mock_github = MagicMock()
    mock_get_github.return_value = mock_github
    mock_list_all_repositories.return_value = repositories_fixture

    runner = CliRunner()
    command = (
        ["list-all-github-repositories", "--stats"]
        if expected_stat
        else ["list-all-github-repositories"]
    )
    result = runner.invoke(cli, command)

    assert result.exit_code == 0
    mock_print_repositories.assert_called_once_with(repositories_fixture, expected_stat)


@pytest.mark.parametrize("expected_stat", [True, False])
@patch("gitea_github_sync.cli.print_repositories", autospec=True)
@patch("gitea_github_sync.cli.gitea.get_gitea", autospec=True)
def test_list_all_gitea_repositories(
    mock_get_gitea: MagicMock,
    mock_print_repositories: MagicMock,
    expected_stat: bool,
    repositories_fixture: List[Repository],
) -> None:
    mock_gitea = MagicMock()
    mock_get_gitea.return_value = mock_gitea
    mock_gitea.get_repos.return_value = repositories_fixture

    runner = CliRunner()
    command = (
        ["list-all-gitea-repositories", "--stats"]
        if expected_stat
        else ["list-all-gitea-repositories"]
    )
    result = runner.invoke(cli, command)

    assert result.exit_code == 0
    mock_print_repositories.assert_called_once_with(repositories_fixture, expected_stat)


@patch("sys.stdout", new_callable=StringIO)
def test_print_repositories_without_stats(
    stdout: StringIO,
    repositories_fixture: List[Repository],
) -> None:

    print_repositories(repositories_fixture, False)
    assert stdout.getvalue() == "some-team/a-repo\nsome-team/b-repo\nsome-team/c-repo\n"


@patch("sys.stdout", new_callable=StringIO)
def test_print_repositories(stdout: StringIO, repositories_fixture: List[Repository]) -> None:

    print_repositories(repositories_fixture, True)
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

    assert stdout.getvalue() == expected_result