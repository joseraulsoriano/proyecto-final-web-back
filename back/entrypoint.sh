#!/bin/bash
set -e

echo "Esperando a que PostgreSQL esté listo..."
until pg_isready -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" 2>/dev/null; do
  echo "PostgreSQL no está listo, esperando..."
  sleep 2
done

echo "PostgreSQL está listo!"

# Aplicar migraciones
echo "Aplicando migraciones..."
python manage.py makemigrations --noinput || echo "No hay cambios en las migraciones"
python manage.py migrate --noinput || {
    echo "Error en migraciones. Limpiando y reiniciando..."
    python manage.py migrate --run-syncdb
}

# Intentar crear superusuario
echo "Verificando creación de superusuario..."
python manage.py shell << 'EOF' || true
import os
import django
django.setup()

try:
    from accounts.models import User
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@campusforum.com')
    
    if not User.objects.filter(email=admin_email).exists():
        print("Creando superusuario...")
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        User.objects.create_superuser(
            email=admin_email,
            password=admin_password,
            first_name='Admin',
            last_name='User'
        )
        print("Superusuario creado exitosamente!")
    else:
        print("Superusuario ya existe")
except Exception as e:
    print(f"No se pudo crear superusuario: {e}")
    print("Puedes crear uno manualmente más tarde con: docker-compose exec web python manage.py createsuperuser")
EOF

echo "Iniciando servidor..."
exec "$@"
