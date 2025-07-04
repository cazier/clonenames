FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Upgrade pip and system packages to reduce vulnerabilities
# RUN apt-get update && \
#     apt-get upgrade -y && \
#     apt-get install -y --no-install-recommends gcc build-essential && \
#     python3 -m pip install --upgrade pip && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN uv sync --locked --no-dev

EXPOSE 5000

CMD ["uv", "run", "clonenames"]
