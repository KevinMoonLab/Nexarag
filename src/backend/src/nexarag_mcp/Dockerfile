FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN pip install -e /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
CMD ["python", "nexarag_mcp/main.py"]