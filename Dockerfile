FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=shop_bot.settings
ENV DATA_DIR=/app/data

# Set work directory
WORKDIR /app

# Install system dependencies for piper-tts
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY shop_bot/ .

# Create data directory for SQLite persistence
RUN mkdir -p /app/data

# Download Piper TTS voice model at build time
RUN python -c "from assistant.tts import download_voice; download_voice()"

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 42069

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:42069"]
