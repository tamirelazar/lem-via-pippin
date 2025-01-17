# Devcontainer Configurations for Pippin

Welcome to the `.devcontainer` directory! Here you'll find Dockerfiles and devcontainer configurations that are essential for setting up your Pippin development environment. Below is a brief overview and how you can utilize them effectively.

These configurations can be used with Codespaces and locally.

## GitHub Codespaces (currently disabled by the organization)

After you fork the repo, navigate to:
https://codespaces.new/{your_github_id}/pipping-draft?quickstart=1

For example:
https://codespaces.new/sonichi/pipping-draft?quickstart=1

## Developing Pippin with Local Devcontainers

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Visual Studio Code Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Getting Started

1. Open the project in Visual Studio Code.
2. Press `Ctrl+Shift+P` and select `Dev Containers: Reopen in Container`.
3. Select the desired python environment and wait for the container to build.
4. Once the container is built, you can start developing Pippin.

### Troubleshooting Common Issues

- Check Docker daemon, port conflicts, and permissions issues.

### Additional Resources

For more information on Docker usage and best practices, refer to the [official Docker documentation](https://docs.docker.com).
