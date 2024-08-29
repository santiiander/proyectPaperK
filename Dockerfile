# Usa una imagen base de Python
FROM python:3.9-slim

# Instala las dependencias del sistema necesarias para mysqlclient
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requisitos
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación
COPY . .

# Expone el puerto en el que la aplicación correrá
EXPOSE 8000

# Define el comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
