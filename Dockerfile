# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . /app

# Instalar dependencias del sistema (si son necesarias, por ejemplo libmpv)
# RUN apt-get update && apt-get install -y libmpv-dev

# Instalar las dependencias de Python necesarias (requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que correrá la app
EXPOSE 8000

# Comando para ejecutar la aplicación (ajustado a tu caso)
CMD ["python", "main.py"]
