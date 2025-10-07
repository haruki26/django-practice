#!/bin/bash

sudo find /app -path /app/docker/mysql/data -prune -o -exec chown vscode:vscode {} +

uv sync
uv pip compile pyproject.toml > requirements.txt
