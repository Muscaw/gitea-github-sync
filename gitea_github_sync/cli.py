import click
from rich import print

from . import github


@click.group()
def cli() -> None:
    pass


@click.option("--stats", is_flag=True)
@cli.command()
def list_all_repositories(stats: bool) -> None:
    gh = github.get_github()
    repos = github.list_all_repositories(gh)
    for repo in repos:
        print(f"[b]{repo.get_org_name()}[/]/{repo.get_repo_name()}")

    if stats:
        print()
        print("[b]Repository stats[/]")
        number_public_repos = sum(
            [1 if repo.visibility == github.Visibility.PUBLIC else 0 for repo in repos]
        )
        number_private_repos = sum(
            [1 if repo.visibility == github.Visibility.PRIVATE else 0 for repo in repos]
        )
        number_unknown_repos = len(repos) - number_public_repos - number_private_repos
        print(f"Number of public repos identified: [b red]{number_public_repos}[/]")
        print(f"Number of private repos identified: [b red]{number_private_repos}[/]")
        print(f"Number of unknown repos identified: [b red]{number_unknown_repos}[/]")
        print(f"Total number of repos identified: [b red]{len(repos)}[/]")
