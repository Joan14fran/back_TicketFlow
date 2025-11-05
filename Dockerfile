# 1. Imagen Base
FROM python:3.11-slim

# 2. Variables de Entorno
ENV PYTHONUNBUFFERED=1

# 3. Directorio de Trabajo
WORKDIR /app

# 4. Instalar Dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

# 5. Copiar el Código
COPY . .

# 6. Comando de Ejecución
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
