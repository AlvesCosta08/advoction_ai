# Usa imagem oficial do Python
FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY web-container/requirements.txt .
COPY web-container/app.py .
COPY web-container/templates ./templates


# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta 5000
EXPOSE 5000

# Comando para rodar o app
CMD ["python", "app.py"]