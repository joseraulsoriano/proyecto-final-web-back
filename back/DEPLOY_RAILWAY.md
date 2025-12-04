# Guía de Despliegue del Backend en Railway

## Pasos para desplegar en Railway

### 1. Crear cuenta en Railway
- Ve a https://railway.app
- Inicia sesión con GitHub

### 2. Crear un nuevo proyecto
- Click en "New Project"
- Selecciona "Deploy from GitHub repo"
- Conecta tu repositorio: `joseraulsoriano/Proyecto-Final-Web`
- Selecciona la carpeta `back` como raíz del proyecto

### 3. Configurar la base de datos PostgreSQL
- En tu proyecto de Railway, click en "+ New"
- Selecciona "Database" → "Add PostgreSQL"
- Railway creará automáticamente una base de datos PostgreSQL

### 4. Configurar variables de entorno
En la sección "Variables" de tu servicio web, agrega:

```
DB_HOST=<valor de PGHOST de la base de datos>
DB_PORT=<valor de PGPORT de la base de datos>
DB_NAME=<valor de PGDATABASE de la base de datos>
DB_USER=<valor de PGUSER de la base de datos>
DB_PASSWORD=<valor de PGPASSWORD de la base de datos>
SECRET_KEY=<genera una clave secreta aleatoria>
DEBUG=False
ALLOWED_HOSTS=<tu-dominio-railway.app,*.railway.app>
```

**Nota**: Railway proporciona estas variables automáticamente. Puedes copiarlas desde la pestaña "Variables" de tu servicio de base de datos.

### 5. Configurar el puerto
Railway asigna un puerto dinámicamente. Necesitas actualizar tu `Dockerfile` o usar la variable de entorno `PORT`.

**Opción A: Modificar el Dockerfile** (recomendado)
Cambiar el CMD para usar la variable PORT:

```dockerfile
CMD ["sh", "-c", "python manage.py migrate && gunicorn campus_forum.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
```

**Opción B: Usar railway.json**
Crear un archivo `railway.json` en la raíz de `back/`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn campus_forum.wsgi:application --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 6. Configurar settings.py para producción
Asegúrate de que `campus_forum/settings.py` tenga:

```python
import os
from dotenv import load_dotenv

load_dotenv()

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
```

### 7. Actualizar CORS en settings.py
Agregar el dominio de Railway a CORS_ALLOWED_ORIGINS:

```python
CORS_ALLOWED_ORIGINS = [
    "https://tu-frontend.vercel.app",
    "http://localhost:4200",  # Para desarrollo local
]
```

### 8. Desplegar
- Railway detectará automáticamente el Dockerfile
- Hará el build y deploy automáticamente
- Obtendrás una URL como: `https://tu-proyecto.railway.app`

### 9. Ejecutar migraciones
Después del primer deploy, ejecuta las migraciones:
- Ve a la pestaña "Deployments"
- Click en el deployment más reciente
- Abre la terminal y ejecuta: `python manage.py migrate`

O agrega esto al entrypoint.sh para que se ejecute automáticamente.

### 10. Actualizar la URL del backend en Vercel
En Vercel, actualiza la variable de entorno:
- `NG_APP_API_URL` = `https://tu-proyecto.railway.app/api`

## Alternativa: Render.com

Si prefieres Render:

1. Ve a https://render.com
2. Crea una cuenta con GitHub
3. "New" → "Web Service"
4. Conecta tu repositorio
5. Configuración:
   - **Root Directory**: `back`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn campus_forum.wsgi:application --bind 0.0.0.0:$PORT`
6. Agrega una base de datos PostgreSQL desde "New" → "PostgreSQL"
7. Configura las variables de entorno igual que en Railway

## Notas importantes

- **Gunicorn**: Ya está en requirements.txt, perfecto para producción
- **Static files**: Si usas archivos estáticos, configura `STATIC_ROOT` y usa WhiteNoise o un servicio de CDN
- **Media files**: Para archivos subidos por usuarios, usa un servicio como AWS S3, Cloudinary, o Railway Volumes
- **SSL**: Railway y Render proporcionan SSL automáticamente



