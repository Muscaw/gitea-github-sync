from typing import List

import click
from rich import print

from . import config, gitea, github, repository


@click.group()
def cli() -> None:
    pass


def print_repositories(repos: List[repository.Repository], display_stats: bool) -> None:
    for repo in repos:
        print(f"[b]{repo.get_org_name()}[/]/{repo.get_repo_name()}")

    if display_stats:
        print()
        print("[b]Repository stats[/]")
        number_public_repos = sum(
            1 if repo.visibility == repository.Visibility.PUBLIC else 0 for repo in repos
        )
        number_private_repos = sum(
            1 if repo.visibility == repository.Visibility.PRIVATE else 0 for repo in repos
        )
        number_unknown_repos = len(repos) - number_public_repos - number_private_repos
        print(f"Number of public repos identified: [b red]{number_public_repos}[/]")
        print(f"Number of private repos identified: [b red]{number_private_repos}[/]")
        print(f"Number of unknown repos identified: [b red]{number_unknown_repos}[/]")
        print(f"Total number of repos identified: [b red]{len(repos)}[/]")


@click.option("--stats", is_flag=True)
@cli.command()
def list_all_github_repositories(stats: bool) -> None:
    gh = github.get_github()
    repos = github.list_all_repositories(gh)
    print_repositories(repos, stats)


@click.option("--stats", is_flag=True)
@cli.command()
def list_all_gitea_repositories(stats: bool) -> None:
    gt = gitea.get_gitea()
    repos = gt.get_repos()
    print_repositories(repos, stats)


@cli.command()
@click.argument("full_repo_name")
def migrate_repo(full_repo_name: str) -> None:
    conf = config.load_config()
    gt = gitea.get_gitea()
    gh = github.get_github()
    github_repos = github.list_all_repositories(gh)
    try:
        repo = next((repo for repo in github_repos if repo.full_repo_name == full_repo_name))
    except StopIteration:
        print(f"[b red]Repository {full_repo_name} does not exist on Github[/]")
        raise click.Abort()

    gt.migrate_repo(repo=repo, github_token=conf.github_token)
