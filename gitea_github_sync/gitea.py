from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests

from gitea_github_sync import config

from .repository import Repository, Visibility


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


def get_gitea(conf: Optional[config.Config] = None) -> Gitea:
    if conf is None:
        conf = config.load_config()
    return Gitea(api_url=conf.gitea_api_url, api_token=conf.gitea_token)
