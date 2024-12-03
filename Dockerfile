FROM python:3.11-slim

#Directorio
WORKDIR /app

COPY . /app

#Instalar dependencias que necesite y libreria libmpv
RUN apt-get update && apt-get install -y libmpv-dev

#Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

#Puerto
EXPOSE 8000

#Comando para ejecutar la App
CMD ["python", "main.py"]
