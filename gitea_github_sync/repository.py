from __future__ import annotations

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
