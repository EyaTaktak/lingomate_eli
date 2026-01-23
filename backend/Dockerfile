# 1. Utiliser une image Python légère
FROM python:3.10-slim

# 2. Installer FFmpeg et les dépendances système
# Ces outils sont nécessaires pour que pydub puisse traiter le WebM/WAV
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Définir le dossier de travail dans le conteneur
WORKDIR /app

# 4. Copier le fichier des dépendances
COPY requirements.txt .

# 5. Installer les bibliothèques Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copier tout le reste du code backend
COPY . .

# 7. Exposer le port que FastAPI utilise (par défaut 8000)
EXPOSE 8000

# 8. Commande de lancement (Uvicorn)
# On écoute sur 0.0.0.0 pour que le serveur soit accessible de l'extérieur
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]