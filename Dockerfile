# 1. Version fixée (Pinning)
FROM python:3.11-slim-bookworm

# 2. Sécurité système
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. Installation des dépendances (optimisée pour le cache)
COPY web/requirements.txt ./web/
RUN pip install --no-cache-dir -r web/requirements.txt

# 4. Copie du code (utilisera le .dockerignore automatiquement)
COPY . .

# 5. Création d'un utilisateur non-root (Indispensable pour la Mission 4)
RUN useradd -m devsecuser && chown -R devsecuser /app
USER devsecuser

# 6. Exposition du port web uniquement (Réduction surface d'attaque)
EXPOSE 5000

# Se placer directement là où est le code
WORKDIR /app/web
# Lancer l'app qui est maintenant dans le dossier courant
CMD ["python", "app.py"]