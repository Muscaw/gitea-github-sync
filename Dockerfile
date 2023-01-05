FROM python:3.11

RUN useradd -m python-user
USER python-user

WORKDIR /app

ENV PATH="${PATH}:/home/python-user/.local/bin/"

COPY gitea_github_sync/ /app/gitea_github_sync
COPY README.md poetry.lock pyproject.toml /app/
COPY docker/config.yml /home/python-user/.config/gitea-github-sync/config.yml

RUN pip install poetry && poetry install

ENTRYPOINT ["poetry", "run", "python", "-m", "gitea_github_sync"]
