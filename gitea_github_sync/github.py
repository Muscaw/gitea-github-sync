from __future__ import annotations

from typing import List, Optional

from github import Github

from . import config
from .repository import Repository, Visibility


def get_github(conf: Optional[config.Config] = None) -> Github:
    if conf is None:
        conf = config.load_config()
    return Github(login_or_token=conf.github_token)


def list_all_repositories(gh: Github) -> List[Repository]:
    repos = gh.get_user().get_repos()
    return [
        Repository(
            full_repo_name=repo.full_name,
            visibility=Visibility.from_str(repo.visibility),
        )
        for repo in repos
    ]
