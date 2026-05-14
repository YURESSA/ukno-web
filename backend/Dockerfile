FROM python:3.10-slim AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY .. ./backend

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "python -m backend.app init_db && echo 'Preparing seed data' && python -m backend.app seed_reference_data && exec gunicorn -w 2 -b 0.0.0.0:5000 backend.wsgi:app --timeout 90"]
