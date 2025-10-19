FROM mcr.microsoft.com/devcontainers/python:3.12

# Switch to vscode user
USER vscode

# Install uv into ~/.local/bin for vscode
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Make sure ~/.local/bin is on PATH
ENV PATH="/home/vscode/.local/bin:${PATH}"