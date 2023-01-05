import textwrap
from io import StringIO
from typing import List
from unittest.mock import MagicMock, PropertyMock, call, patch

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


@patch("gitea_github_sync.cli.config.load_config", autospec=True)
@patch("gitea_github_sync.cli.github.list_all_repositories", autospec=True)
@patch("gitea_github_sync.cli.github.get_github", autospec=True)
@patch("gitea_github_sync.cli.gitea.get_gitea", autospec=True)
def test_migrate_repo(
    mock_get_gitea: MagicMock,
    mock_get_github: MagicMock,
    mock_list_all_repositories: MagicMock,
    mock_load_config: MagicMock,
    repositories_fixture: List[Repository],
) -> None:
    expected_repo = Repository("Muscaw/gitea-github-sync", Visibility.PRIVATE)
    expected_github_token = "some-github-token"

    type(mock_load_config.return_value).github_token = PropertyMock(
        return_value=expected_github_token
    )
    mock_list_all_repositories.return_value = repositories_fixture + [expected_repo]

    runner = CliRunner()
    command = ["migrate-repo", "Muscaw/gitea-github-sync"]
    result = runner.invoke(cli, command)

    assert result.exit_code == 0
    mock_list_all_repositories.assert_called_once_with(mock_get_github.return_value)
    mock_get_gitea.return_value.migrate_repo.assert_called_once_with(
        repo=expected_repo, github_token=expected_github_token
    )


@patch("gitea_github_sync.cli.config.load_config", autospec=True)
@patch("gitea_github_sync.cli.github.list_all_repositories", autospec=True)
@patch("gitea_github_sync.cli.github.get_github", autospec=True)
@patch("gitea_github_sync.cli.gitea.get_gitea", autospec=True)
def test_migrate_repo_no_match(
    mock_get_gitea: MagicMock,
    mock_get_github: MagicMock,
    mock_list_all_repositories: MagicMock,
    mock_load_config: MagicMock,
    repositories_fixture: List[Repository],
) -> None:
    mock_list_all_repositories.return_value = repositories_fixture
    repo_name = "Muscaw/gitea-github-sync"

    runner = CliRunner()
    command = ["migrate-repo", repo_name]
    result = runner.invoke(cli, command)

    assert result.exit_code != 0
    assert "Aborted!" in result.stdout
    assert f"Repository {repo_name} does not exist on Github" in result.stdout
    mock_list_all_repositories.assert_called_once_with(mock_get_github.return_value)
    mock_get_gitea.return_value.migrate_repo.assert_not_called()
    mock_load_config.assert_called_once()


NO_REPOS: List[Repository] = []
MULTIPLE_REPOS = [
    Repository("some-team/a-repo", Visibility.PUBLIC),
    Repository("some-team/b-repo", Visibility.PRIVATE),
    Repository("some-team/c-repo", Visibility.UNKNOWN),
]


@pytest.mark.parametrize(
    "repos_to_sync, expected_output",
    [
        (
            NO_REPOS,
            textwrap.dedent(
                """\
                Starting migration for 0 repos
                Migrated 0 repos successfully
            """
            ),
        ),
        (
            MULTIPLE_REPOS,
            textwrap.dedent(
                """\
                Starting migration for 3 repos
                Migrating some-team/a-repo
                Migrating some-team/b-repo
                Migrating some-team/c-repo
                Migrated 3 repos successfully
                """
            ),
        ),
    ],
)
@patch("gitea_github_sync.cli.migration.list_missing_github_repos", autospec=True)
@patch("gitea_github_sync.cli.config.load_config", autospec=True)
@patch("gitea_github_sync.cli.github.list_all_repositories", autospec=True)
@patch("gitea_github_sync.cli.github.get_github", autospec=True)
@patch("gitea_github_sync.cli.gitea.get_gitea", autospec=True)
def test_sync(
    mock_get_gitea: MagicMock,
    mock_get_github: MagicMock,
    mock_list_all_repositories: MagicMock,
    mock_load_config: MagicMock,
    mock_list_missing_github_repos: MagicMock,
    repos_to_sync: List[Repository],
    expected_output: str,
) -> None:
    expected_github_token = "some-github-token"

    type(mock_load_config.return_value).github_token = PropertyMock(
        return_value=expected_github_token
    )
    mock_list_missing_github_repos.return_value = repos_to_sync

    runner = CliRunner()
    command = ["sync"]
    result = runner.invoke(cli, command)

    assert result.exit_code == 0
    assert result.stdout == expected_output
    mock_load_config.assert_called_once()
    mock_list_all_repositories.assert_called_once_with(mock_get_github.return_value)
    mock_list_missing_github_repos.assert_called_once_with(
        gh_repos=mock_list_all_repositories.return_value,
        gitea_repos=mock_get_gitea.return_value.get_repos.return_value,
    )
    mock_get_gitea.return_value.migrate_repo.assert_has_calls(
        [call(repo=repo, github_token=expected_github_token) for repo in repos_to_sync]
    )


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
