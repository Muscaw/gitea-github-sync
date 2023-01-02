from dataclasses import dataclass
from typing import List
from unittest.mock import MagicMock, patch

import pytest
from github import Github

from gitea_github_sync.config import Config
from gitea_github_sync.github import get_github, list_all_repositories
from gitea_github_sync.repository import Repository, Visibility

from .test_config import VALID_CONFIG


@pytest.fixture
def conf_fixture() -> Config:
    return VALID_CONFIG


@pytest.mark.parametrize(
    "str_value, expected",
    [
        ("public", Visibility.PUBLIC),
        ("private", Visibility.PRIVATE),
        ("unknown", Visibility.UNKNOWN),
        ("random_value", Visibility.UNKNOWN),
    ],
)
def test_visibility_from_str(str_value: str, expected: Visibility) -> None:
    result = Visibility.from_str(str_value)
    assert result == expected


@pytest.mark.parametrize(
    "expected_org, repo",
    [
        ("team", Repository(full_repo_name="team/some-repo", visibility=Visibility.UNKNOWN)),
        (
            "some-team",
            Repository(full_repo_name="some-team/some-repo", visibility=Visibility.UNKNOWN),
        ),
    ],
)
def test_repository_get_org_name(expected_org: str, repo: Repository) -> None:
    org_name = repo.get_org_name()
    assert org_name == expected_org


@pytest.mark.parametrize(
    "expected_repo_name, repo",
    [
        ("repo", Repository(full_repo_name="team/repo", visibility=Visibility.UNKNOWN)),
        (
            "some-repo",
            Repository(full_repo_name="some-team/some-repo", visibility=Visibility.UNKNOWN),
        ),
    ],
)
def test_repository_get_repo_name(expected_repo_name: str, repo: Repository) -> None:
    repo_name = repo.get_repo_name()
    assert repo_name == expected_repo_name


@patch("gitea_github_sync.github.Github", autospec=True)
def test_github(mock_github: MagicMock, conf_fixture: Config) -> None:
    gh = get_github(conf_fixture)

    assert gh == mock_github.return_value
    mock_github.assert_called_once_with(conf_fixture.github_token)


@patch("gitea_github_sync.github.config.load_config", autospec=True)
@patch("gitea_github_sync.github.Github", autospec=True)
def test_github_default_value(
    mock_github: MagicMock, mock_load_config: MagicMock, conf_fixture: Config
) -> None:
    mock_load_config.return_value = conf_fixture
    gh = get_github()

    assert gh == mock_github.return_value
    mock_github.assert_called_once_with(conf_fixture.github_token)
    mock_load_config.assert_called_once()


@dataclass(frozen=True)
class MockGithubRepository:
    full_name: str
    visibility: str


@pytest.mark.parametrize(
    "gh_repos, expected_repos",
    [
        (
            [
                MockGithubRepository(full_name="a/a-repo", visibility="public"),
                MockGithubRepository(full_name="b/a-repo", visibility="private"),
                MockGithubRepository(full_name="c/a-repo", visibility="unknown"),
                MockGithubRepository(full_name="d/a-repo", visibility="something-else"),
            ],
            [
                Repository(full_repo_name="a/a-repo", visibility=Visibility.PUBLIC),
                Repository(full_repo_name="b/a-repo", visibility=Visibility.PRIVATE),
                Repository(full_repo_name="c/a-repo", visibility=Visibility.UNKNOWN),
                Repository(full_repo_name="d/a-repo", visibility=Visibility.UNKNOWN),
            ],
        ),
        (
            [MockGithubRepository(full_name="some-team/a-repo", visibility="public")],
            [Repository(full_repo_name="some-team/a-repo", visibility=Visibility.PUBLIC)],
        ),
        (
            [],
            [],
        ),
    ],
)
def test_list_all_repositories(
    gh_repos: List[MockGithubRepository], expected_repos: List[Repository]
) -> None:
    mock_gh = MagicMock(spec_set=Github)
    mock_gh.get_user.return_value.get_repos.return_value = gh_repos

    result = list_all_repositories(mock_gh)

    assert result == expected_repos
    mock_gh.get_user.assert_called_once()
    mock_gh.get_user.return_value.get_repos.assert_called_once()
