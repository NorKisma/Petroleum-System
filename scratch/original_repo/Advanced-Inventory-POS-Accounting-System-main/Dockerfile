# ─────────────────────────────────────────────────────────────────────────────
# Dockerfile — Advanced Inventory POS & Accounting System
# Build:   docker build -t rays-pos .
# Run:     docker run -p 5000:5000 rays-pos
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p app/static/uploads

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose the application port
EXPOSE 5000

# Run the application via gunicorn for production
CMD ["python", "wsgi.py"]
