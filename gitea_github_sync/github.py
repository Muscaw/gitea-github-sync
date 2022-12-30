from __future__ import annotations
from typing import List
from github import Github
from . import config
from dataclasses import dataclass
from enum import Flag, auto


class Visibility(Flag):
    PUBLIC = auto()
    PRIVATE = auto()
    UNKNOWN = auto()

    @staticmethod
    def from_str(value: str) -> Visibility:
        if value == "public":
            return Visibility.PUBLIC
        elif value == "private":
            return Visibility.PRIVATE
        else:
            return Visibility.UNKNOWN


@dataclass(frozen=True)
class Repository:
    full_repo_name: str
    visibility: Visibility

    def get_org_name(self) -> str:
        return self.full_repo_name.split("/")[0]

    def get_repo_name(self) -> str:
        return self.full_repo_name.split("/")[1]


def get_github(conf: config.Config = config.load_config()) -> Github:
    return Github(login_or_token=conf.github_token)


def list_all_repositories(gh: Github) -> List[Repository]:
    repos = gh.get_user().get_repos()
    output = []
    for repo in repos:
        output.append(
            Repository(
                full_repo_name=repo.full_name, visibility=Visibility.from_str(repo.visibility)
            )
        )
    return output
