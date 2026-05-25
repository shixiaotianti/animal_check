FROM python:3.13-slim

# Install system dependencies required by OpenCV
RUN apt-get update && apt-get install -y \
    libxcb1 \
    libxkbcommon0 \
    libgl1 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the application
CMD ["/app/.venv/bin/python", "app.py"]
