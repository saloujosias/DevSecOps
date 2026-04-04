# 1. PINNER LA VERSION (Utiliser un digest ou une version précise, pas 'latest')
FROM python:3.11-slim-bookworm

# 2. RÉDUIRE LA SURFACE (Installer uniquement le nécessaire)
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. PRINCIPE DU MOINDRE PRIVILÈGE (Créer un utilisateur non-root)
RUN groupadd -g 10001 appuser && \
    useradd -u 10001 -g appuser appuser
    
COPY . .

# Donner les droits à l'utilisateur sur le dossier app
RUN chown -R appuser:appuser /app

# 4. EXÉCUTER EN NON-ROOT
USER appuser

EXPOSE 5000
CMD ["python", "app.py"]