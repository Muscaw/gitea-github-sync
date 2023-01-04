from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests

from gitea_github_sync import config

from .repository import Repository, Visibility


@dataclass(frozen=True)
class GiteaMigrationError(ValueError):
    full_repo_name: str

    def __str__(self) -> str:
        return f"Could not migrate {self.full_repo_name}"


@dataclass(frozen=True)
class Gitea:
    api_url: str
    api_token: str

    def _get_authorization_header(self) -> Dict[str, str]:
        return {"Authorization": f"token {self.api_token}"}

    def _get_all_pages(self, path: str) -> List[Dict[str, Any]]:
        output = []
        url: Optional[str] = f"{self.api_url}{path}"
        while url is not None:
            auth = self._get_authorization_header()
            result = requests.get(url, headers=auth)
            result.raise_for_status()
            data = result.json()
            output.extend(data)

            url = result.links["next"]["url"] if "next" in result.links else None
        return output

    def get_repos(self) -> List[Repository]:

        repos = self._get_all_pages("/user/repos")
        return [
            Repository(
                repo["full_name"],
                visibility=Visibility.PRIVATE if repo["private"] else Visibility.PUBLIC,
            )
            for repo in repos
        ]

    def migrate_repo(self, repo: Repository, github_token: str) -> None:
        request_data = {
            "auth_token": github_token,
            "clone_addr": f"https://github.com/{repo.full_repo_name}",
            "repo_name": repo.get_repo_name(),
            "service": "github",
            "mirror": True,
            "private": repo.visibility == Visibility.PRIVATE,
        }
        res = requests.post(
            f"{self.api_url}/repos/migrate",
            headers=self._get_authorization_header(),
            json=request_data,
        )
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            raise GiteaMigrationError(repo.full_repo_name) from e


def get_gitea(conf: Optional[config.Config] = None) -> Gitea:
    if conf is None:
        conf = config.load_config()
    return Gitea(api_url=conf.gitea_api_url, api_token=conf.gitea_token)
