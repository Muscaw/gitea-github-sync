# gitea-github-sync docker image

gitea-github-sync is automatically packaged in a docker image and can be pulled with the following command:

`docker pull muscaw/gitea-github-sync:latest`

## Setup

### Setup using environment variables

The docker image contains a configuration file that uses environment variables to configure gitea-github-sync.

You can create a file called _.env_ with the following content:

```
GITHUB_TOKEN=<your-github-token>
GITEA_API_URL=https://<your-gitea-url>/api/v1
GITEA_TOKEN=<your-gitea-token>
``` 

Run the docker image with the env file:

`docker run --rm --env-file .env muscaw/gitea-github-sync:latest sync`

### Mount a configuration file

Create the config.yml file wherever you want and mount it in the docker container:

`docker run --rm -v <location-of-config.yml>:/home/python-user/.config/gitea-github-sync/config.yml muscaw/gitea-github-sync:latest sync`
