#!/bin/bash
set -e

# Instalar dependencias del sistema para psycopg2
apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    || echo "No se pudieron instalar dependencias del sistema (esto es normal en algunos entornos)"

# Instalar dependencias de Python
pip install --upgrade pip
pip install -r requirements.txt

