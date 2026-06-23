FROM python:3.12-slim

# ---------------- ENV ----------------
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# ---------------- SYSTEM DEPENDENCIES ----------------
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# ---------------- REQUIREMENTS (CACHE LAYER) ----------------
COPY requirements.txt /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------------- COPY PROJECT ----------------
COPY . /app/

# ---------------- SAFETY ----------------
# prevent permission issues on Linux servers
RUN useradd -m botuser && chown -R botuser:botuser /app
USER botuser

# ---------------- START BOT ----------------
CMD ["python", "main.py"]
