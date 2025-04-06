# Usa a imagem oficial do Python
FROM python:3.10

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos necessários para o container
COPY . .

# Copia o arquivo .env (se existir)
COPY .env .env

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Instala o pacote python-dotenv para carregar variáveis de ambiente
RUN pip install python-dotenv

# Expõe a porta 5000 para acesso à API
EXPOSE 3000

# Define a variável de ambiente para desativar o buffer de saída
ENV PYTHONUNBUFFERED=1

# Carrega as variáveis de ambiente do .env antes de iniciar a aplicação
CMD ["sh", "-c", "export $(grep -v '^#' .env | xargs) && python main.py"]