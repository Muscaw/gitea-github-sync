from typing import Any, Dict

import responses
from responses import matchers

from gitea_github_sync.gitea import Gitea
from gitea_github_sync.repository import Repository, Visibility

GITEA_BASE_API_URL = "https://gitea.yourinstance.com/api/v1"
GITEA_TOKEN = "your-gitea-token"


def gitea_fixture(custom_params: Dict[str, Any] = dict()) -> Gitea:
    params = {
        "api_url": GITEA_BASE_API_URL,
        "api_token": GITEA_TOKEN,
    }
    params.update(custom_params)
    return Gitea(**params)


@responses.activate
def test_get_repos() -> None:
    gitea = gitea_fixture()

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

    result = gitea.get_repos()
    assert expected_repos == result


@responses.activate
def test_get_repos_multiple_pages() -> None:
    gitea = gitea_fixture()

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

    result = gitea.get_repos()
    assert expected_repos == result
