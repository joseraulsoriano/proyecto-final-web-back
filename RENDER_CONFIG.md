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
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

**Alternativa si falla psycopg2**: Si sigue fallando, usa este comando más completo:
```bash
apt-get update && apt-get install -y libpq-dev gcc || true && pip install --upgrade pip && pip install -r requirements.txt
```

### Start Command (RECOMENDADO - con migraciones)
**Usa este comando que ejecuta las migraciones antes de iniciar el servidor:**
```bash
python manage.py migrate --noinput && gunicorn campus_forum.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

**IMPORTANTE**: 
- Asegúrate de que el comando NO esté duplicado en Render
- Este comando ejecuta las migraciones automáticamente cada vez que se inicia el servicio
- Si las migraciones fallan, el servicio no iniciará (esto es bueno para detectar problemas)

### Start Command (Alternativa - sin migraciones automáticas)
Si prefieres ejecutar las migraciones manualmente:
```bash
gunicorn campus_forum.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

## Pre-Deploy Command
**NO uses Pre-Deploy Command para migraciones** - Las variables de entorno de la base de datos pueden no estar disponibles durante el Pre-Deploy. Usa el Start Command con migraciones en su lugar.

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

