FROM python:3.12.9-slim

# Install Git and other necessary system packages
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.6.10 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml pyproject.toml

COPY uv.lock uv.lock

RUN uv sync --frozen

COPY main.py main.py
COPY utils/ utils/
COPY .env.example .env.example

CMD ["uv", "run", "main.py"]