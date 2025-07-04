FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

COPY . .

RUN uv sync --locked --no-dev

EXPOSE 5000

CMD ["uv", "run", "clonenames"]
