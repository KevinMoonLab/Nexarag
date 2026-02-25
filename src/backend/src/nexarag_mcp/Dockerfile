# syntax=docker/dockerfile:1.7
FROM python:3.11-slim
WORKDIR /app
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
COPY pyproject.toml /tmp/pyproject.toml
RUN --mount=type=cache,target=/root/.cache/pip \
    python -c "import tomllib; from pathlib import Path; p=Path('/tmp/pyproject.toml'); d=tomllib.loads(p.read_text())['project']['dependencies']; Path('/tmp/requirements-runtime.txt').write_text('\\n'.join(d)+'\\n')" \
    && pip install -r /tmp/requirements-runtime.txt
COPY . /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-deps -e /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
CMD ["python", "nexarag_mcp/main.py"]
