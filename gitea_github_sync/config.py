from __future__ import annotations

from pathlib import Path

from piny import PydanticValidator, StrictMatcher, YamlLoader
from pydantic import BaseModel


class Config(BaseModel):
    github_token: str
    gitea_api_url: str
    gitea_token: str


def config_file_location() -> Path:
    return Path.home() / ".config" / "gitea-github-sync" / "config.yml"


def load_config(config_location: Path = config_file_location()) -> Config:

    return Config(
        **YamlLoader(
            path=config_location,
            matcher=StrictMatcher,
            validator=PydanticValidator,
            schema=Config,
        ).load()
    )
