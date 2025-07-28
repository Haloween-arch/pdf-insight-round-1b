# Use slim image to reduce size (~200MB instead of 900MB)
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements & model first (to cache layers)
COPY requirements.txt .
COPY models /app/models

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ /app/

# Run Round 1B entrypoint
CMD ["python", "main_1b.py"]
