# Configuración para Render.com

## Variables de Entorno para el Web Service

Copia estas variables en la sección "Environment Variables" de Render:

### Base de Datos (desde tu servicio PostgreSQL de Render)
```
DB_HOST=<valor de Internal Database Host de Render>
DB_PORT=5432
DB_NAME=<valor de Database de Render>
DB_USER=<valor de User de Render>
DB_PASSWORD=<valor de Password de Render>
```

**Nota**: Render te da estas variables automáticamente. Puedes copiarlas desde la pestaña "Info" de tu servicio PostgreSQL.

### Configuración de Django
```
SECRET_KEY=<genera una clave secreta aleatoria, ejemplo: django-insecure-$(openssl rand -hex 32)>
DEBUG=False
ALLOWED_HOSTS=*.onrender.com,tu-servicio.onrender.com
```

### CORS - Permitir peticiones desde Vercel
```
CORS_ALLOWED_ORIGINS=https://proyecto-final-web-alpha.vercel.app,http://localhost:4200
```

### Opcional: Superusuario Admin
```
ADMIN_EMAIL=admin@campusforum.com
ADMIN_PASSWORD=<tu-contraseña-segura>
```

## Comandos

### Build Command
```
pip install -r requirements.txt
```

### Start Command
```
gunicorn campus_forum.wsgi:application --bind 0.0.0.0:$PORT
```

## Pre-Deploy Command (Opcional)
Si quieres ejecutar migraciones automáticamente antes de cada deploy:
```
python manage.py migrate --noinput
```

## Pasos Adicionales

1. **Después del primer deploy**, ejecuta las migraciones manualmente desde la terminal de Render:
   ```bash
   python manage.py migrate
   ```

2. **Crear superusuario** (si no usaste las variables de entorno):
   ```bash
   python manage.py createsuperuser
   ```

3. **Actualizar la URL del backend en Vercel**:
   - Ve a tu proyecto en Vercel
   - Settings → Environment Variables
   - Actualiza `NG_APP_API_URL` con: `https://tu-servicio.onrender.com/api`

## URL del Backend

Después del deploy, tu backend estará disponible en:
```
https://tu-servicio.onrender.com
```

Y la API en:
```
https://tu-servicio.onrender.com/api
```

