# syntax=docker/dockerfile:1.7
FROM python:3.11-slim
WORKDIR /app
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
COPY pyproject.toml /app/pyproject.toml
RUN --mount=type=cache,target=/root/.cache/pip \
    python -c "import tomllib; from pathlib import Path; p=Path('/app/pyproject.toml'); d=tomllib.loads(p.read_text())['project']['dependencies']; Path('/tmp/requirements-runtime.txt').write_text('\\n'.join(d)+'\\n')" \
    && pip install -r /tmp/requirements-runtime.txt
COPY src /app/src
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-deps -e /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
CMD ["python", "-m", "nexarag_mcp.main"]
