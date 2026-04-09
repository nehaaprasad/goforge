# API image: Python + Go (for validation) + git; SQLite persisted via /data volume.
FROM golang:1.22-bookworm AS golang

FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=golang /usr/local/go /usr/local/go
ENV PATH="/usr/local/go/bin:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY goforge ./goforge

ENV PYTHONUNBUFFERED=1
ENV GOFORGE_REPO_ROOT=/workspace/sandbox-repo
ENV GOFORGE_DB_PATH=/data/goforge.db

EXPOSE 8000

CMD ["uvicorn", "goforge.main:app", "--host", "0.0.0.0", "--port", "8000"]
