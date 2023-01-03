from typing import List

import pytest

from gitea_github_sync.migration import list_missing_github_repos
from gitea_github_sync.repository import Repository, Visibility


def r(org_name: str, repo_name: str) -> Repository:
    return Repository(full_repo_name=f"{org_name}/{repo_name}", visibility=Visibility.PUBLIC)


def team_a_repo(repo_name: str) -> Repository:
    return r(org_name="team-a", repo_name=repo_name)


def team_b_repo(repo_name: str) -> Repository:
    return r(org_name="team-b", repo_name=repo_name)


@pytest.mark.parametrize(
    "gh_repos, gt_repos, expected_diff",
    [
        pytest.param(
            [team_a_repo("a-repo"), team_a_repo("b-repo")],
            [team_b_repo("a-repo"), team_b_repo("b-repo")],
            [],
            id="equal",
        ),
        pytest.param(
            [team_a_repo("a-repo"), team_a_repo("b-repo")],
            [team_b_repo("a-repo")],
            [team_a_repo("b-repo")],
            id="missing-repo-on-gitea",
        ),
        pytest.param(
            [team_a_repo("a-repo"), team_a_repo("b-repo")],
            [team_b_repo("a-repo"), team_b_repo("b-repo"), team_b_repo("c-repo")],
            [],
            id="too-many-repos-on-gitea",
        ),
    ],
)
def test_list_missing_github_repos(
    gh_repos: List[Repository], gt_repos: List[Repository], expected_diff: List[Repository]
) -> None:
    result = list_missing_github_repos(gh_repos=gh_repos, gitea_repos=gt_repos)

    assert result == expected_diff
