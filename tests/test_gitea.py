from unittest.mock import MagicMock, patch

import pytest
import responses
from responses import matchers

from gitea_github_sync.config import Config
from gitea_github_sync.gitea import Gitea, get_gitea
from gitea_github_sync.repository import Repository, Visibility

GITEA_BASE_API_URL = "https://gitea.yourinstance.com/api/v1"
GITEA_TOKEN = "your-gitea-token"


@pytest.fixture
def conf_fixture() -> Config:
    return Config(
        github_token="some-token", gitea_api_url=GITEA_BASE_API_URL, gitea_token=GITEA_TOKEN
    )


@pytest.fixture
def gitea_fixture(conf_fixture: Config) -> Gitea:
    return Gitea(api_url=conf_fixture.gitea_api_url, api_token=conf_fixture.gitea_token)


@responses.activate
def test_get_repos(gitea_fixture: Gitea) -> None:

    json = [
        {"full_name": "some-team/a-repo", "private": True},
        {"full_name": "some-team/b-repo", "private": False},
    ]

    expected_repos = [
        Repository(full_repo_name="some-team/a-repo", visibility=Visibility.PRIVATE),
        Repository(full_repo_name="some-team/b-repo", visibility=Visibility.PUBLIC),
    ]
    responses.get(
        f"{GITEA_BASE_API_URL}/user/repos",
        match=[matchers.header_matcher({"Authorization": f"token {GITEA_TOKEN}"})],
        json=json,
    )

    result = gitea_fixture.get_repos()
    assert expected_repos == result


@responses.activate
def test_get_repos_multiple_pages(gitea_fixture: Gitea) -> None:

    json_1 = [
        {"full_name": "some-team/a-repo", "private": True},
        {"full_name": "some-team/b-repo", "private": False},
    ]
    json_2 = [
        {"full_name": "some-team/c-repo", "private": True},
        {"full_name": "some-team/d-repo", "private": False},
    ]
    json_3 = [
        {"full_name": "some-team/e-repo", "private": True},
        {"full_name": "some-team/f-repo", "private": False},
    ]

    expected_repos = [
        Repository(full_repo_name="some-team/a-repo", visibility=Visibility.PRIVATE),
        Repository(full_repo_name="some-team/b-repo", visibility=Visibility.PUBLIC),
        Repository(full_repo_name="some-team/c-repo", visibility=Visibility.PRIVATE),
        Repository(full_repo_name="some-team/d-repo", visibility=Visibility.PUBLIC),
        Repository(full_repo_name="some-team/e-repo", visibility=Visibility.PRIVATE),
        Repository(full_repo_name="some-team/f-repo", visibility=Visibility.PUBLIC),
    ]
    responses.get(
        f"{GITEA_BASE_API_URL}/user/repos",
        match=[matchers.header_matcher({"Authorization": f"token {GITEA_TOKEN}"})],
        json=json_1,
        headers={
            "link": (
                f'<{GITEA_BASE_API_URL}/user/repos?page=2>; rel="next",'
                + f'<{GITEA_BASE_API_URL}/user/repos?page=3>; rel="last"'
            )
        },
    )
    responses.get(
        f"{GITEA_BASE_API_URL}/user/repos?page=2",
        match=[matchers.header_matcher({"Authorization": f"token {GITEA_TOKEN}"})],
        json=json_2,
        headers={
            "link": (
                f'<{GITEA_BASE_API_URL}/user/repos?page=3>; rel="next",'
                + f'<{GITEA_BASE_API_URL}/user/repos?page=3>; rel="last",'
                + f'<{GITEA_BASE_API_URL}/user/repos?page=1>; rel="first",'
                + f'<{GITEA_BASE_API_URL}/user/repos?page=1>; rel="prev"'
            )
        },
    )
    responses.get(
        f"{GITEA_BASE_API_URL}/user/repos?page=3",
        match=[matchers.header_matcher({"Authorization": f"token {GITEA_TOKEN}"})],
        json=json_3,
        headers={
            "link": (
                f'<{GITEA_BASE_API_URL}/user/repos?page=1>; rel="first",'
                + f'<{GITEA_BASE_API_URL}/user/repos?page=1>; rel="prev"'
            )
        },
    )

    result = gitea_fixture.get_repos()
    assert expected_repos == result


def test_gitea(gitea_fixture: Gitea, conf_fixture: Config) -> None:
    gt = get_gitea(conf_fixture)

    assert gt == gitea_fixture


@patch("gitea_github_sync.gitea.config.load_config", autospec=True)
def test_gitea_default_value(
    mock_load_config: MagicMock, gitea_fixture: Gitea, conf_fixture: Config
) -> None:
    mock_load_config.return_value = conf_fixture
    gt = get_gitea()

    assert gt == gitea_fixture
    mock_load_config.assert_called_once()
