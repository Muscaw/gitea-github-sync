from __future__ import annotations
from piny import YamlLoader, PydanticValidator, StrictMatcher
from pydantic import BaseModel
from pathlib import Path


class Config(BaseModel):
    github_token: str
    gitea_token: str


def config_file_location() -> Path:
    return Path.home() / ".config" / "gitea-mirror" / "config.yml"


def load_config(config_location: Path = config_file_location()) -> Config:

    return Config(
        **YamlLoader(
            path=config_location,
            matcher=StrictMatcher,
            validator=PydanticValidator,
            schema=Config,
        ).load()
    )
