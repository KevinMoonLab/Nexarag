# syntax=docker/dockerfile:1.7
FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV UV_SYSTEM_PYTHON=1

COPY pyproject.toml /app/pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    python -c "import tomllib; from pathlib import Path; p=Path('/app/pyproject.toml'); d=tomllib.loads(p.read_text())['project']['dependencies']; Path('/tmp/requirements-runtime.txt').write_text('\\n'.join(d)+'\\n')" \
    && uv pip install --system -r /tmp/requirements-runtime.txt

COPY src /app/src

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --no-deps -e /app

ENV PYTHONPATH=/app/src

CMD ["python", "-m", "kg.main"]
