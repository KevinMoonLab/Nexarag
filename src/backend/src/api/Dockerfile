# syntax=docker/dockerfile:1.7
FROM python:3.11-slim

WORKDIR /app
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . /app

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-deps -e /app

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000"]
