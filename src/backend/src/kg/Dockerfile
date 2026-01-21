FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN pip install -e /app

ENV PYTHONPATH=/app

CMD ["python", "kg/main.py"]