FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para Pillow y PostgreSQL
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . .

# Hacer ejecutable el script de entrypoint
RUN chmod +x entrypoint.sh

# Exponer puerto
EXPOSE 8000

# Ejecutar entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]