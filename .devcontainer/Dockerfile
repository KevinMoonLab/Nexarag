# Use a Python base image with necessary system dependencies
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install necessary OS dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install pip dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir jupyterlab

# Copy the application code
COPY . /app

# Install the application in editable mode

RUN pip install -e /app/src

# Set Python path
ENV PYTHONPATH=/app

EXPOSE 8888

# Default command to keep container running
# CMD ["bash"]
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
