# Imagen base
FROM python:3.13.5-slim-bookworm

# reemplace a esta que estaba:
# FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requisitos
COPY ./requirements.txt /app/requirements.txt

# Instala las dependencias
RUN apt-get update
RUN apt-get install -y libpq-dev gcc
RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# Copia el proyecto
COPY ./ /app

# no aparece gunicorn en requirements.txt porque es solo para Linux
RUN pip install gunicorn

# Expone el puerto para el servidor de desarrollo
EXPOSE 8000

# Ejecutar collectstatic
RUN python manage.py collectstatic --noinput

# Comando para iniciar el servidor Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "proyecto_01.wsgi:application"]


