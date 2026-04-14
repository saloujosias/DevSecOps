FROM python:3.11-slim-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m devsecuser

WORKDIR /app

COPY web/requirements.txt ./web/
RUN pip install --no-cache-dir -r web/requirements.txt

COPY --chown=devsecuser:devsecuser . .

USER devsecuser

WORKDIR /app/web

EXPOSE 5000

CMD ["python", "app.py"]