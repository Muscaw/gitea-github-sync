from typing import List

from gitea_github_sync.repository import Repository


def list_missing_github_repos(
    gh_repos: List[Repository], gitea_repos: List[Repository]
) -> List[Repository]:
    gitea_repos_by_name = [repo.get_repo_name() for repo in gitea_repos]
    return [repo for repo in gh_repos if repo.get_repo_name() not in gitea_repos_by_name]
