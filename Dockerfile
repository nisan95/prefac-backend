FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système (gcc pour certaines dépendances Python)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances
COPY requirements.txt .

# Création de l'environnement virtuel et installation des dépendances
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Variables d'environnement Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Port exposé
EXPOSE 5000

# Commande de démarrage
CMD ["/bin/bash", "-c", ". venv/bin/activate && flask run --host=0.0.0.0 --reload"]