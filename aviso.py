import requests
from telegram import Bot
import json
import os
from flask import Flask
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from logging import getLogger, StreamHandler, INFO
import asyncio

from pytz import timezone

scheduler = AsyncIOScheduler(timezone=timezone('UTC'))

app = Flask(__name__)

# Configurações do logger
logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(StreamHandler())

# Configurações do Telegram (usar variáveis de ambiente)
BOT_TOKEN = '7514578178:AAGXKsSqf8bY2GUhG5F32XADph_MZ5CJrzc'
CHAT_ID = '5782098350'


if not BOT_TOKEN or not CHAT_ID:
    logger.error("BOT_TOKEN e CHAT_ID devem ser definidos nas variáveis de ambiente.")
    exit(1)

# URL a ser monitorada
URL = 'https://eventos.unochapeco.edu.br/eventos/'

# Payload JSON para a requisição POST
payload = {
    "model": "{\"cidade\":null,\"filtroCampoTexto\":\"PUG\",\"ano\":null,\"unidade\":null,\"formatoEvento\":\"\"}"
}

# Caminho do arquivo onde as respostas já enviadas serão armazenadas
STORAGE_FILE = 'notified_responses.json'

# Função para carregar as respostas já notificadas
def load_notified_responses():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                # Se o arquivo estiver vazio ou corrompido, retorna uma lista vazia
                return []
    return []

# Função para salvar as respostas já notificadas
def save_notified_response(response_text):
    notified_responses = load_notified_responses()
    notified_responses.append(response_text)
    with open(STORAGE_FILE, 'w') as file:
        json.dump(notified_responses, file)

# Função para verificar a presença do texto específico nos resultados da resposta
async def verificar_site():
    try:
        response = requests.post(URL, json=payload)
        if response.status_code == 200:
            response_text = response.text
            notified_responses = load_notified_responses()

            # Verifica se a resposta já foi notificada
            if response_text not in notified_responses:
                if "PUG" in response_text:
                    save_notified_response(response_text)
                    logger.info('Texto "PUG" encontrado no site.')
                    await send_message_to_telegram('O texto "PUG" foi encontrado no site!')
                else:
                    logger.info('Texto "PUG" não encontrado na resposta.')
            else:
                logger.info('Resposta já notificada anteriormente.')
        else:
            logger.error(f"Falha ao acessar o site. Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Erro ao verificar o site: {e}")

# Função para enviar uma mensagem no Telegram
async def send_message_to_telegram(text):
    try:
        bot = Bot(token='8069837006:AAFhgqqv0SNkzUDLgBEgpRKFAy_Ev5WR59A')
        await bot.send_message(chat_id='5782098350', text='text')
        logger.info('Mensagem enviada para o Telegram.')
    except Exception as e:
        logger.error(f'Erro ao enviar mensagem para o Telegram: {e}')

# Configuração do agendador assíncrono
scheduler = AsyncIOScheduler()
scheduler.add_job(verificar_site, 'interval', minutes=5)
scheduler.start()

# Iniciar o loop de eventos
loop = asyncio.get_event_loop()

# Rota principal
@app.route('/')
def home():
    return "Aplicativo Flask está em execução."

# Encerrar o agendador ao finalizar o aplicativo
import atexit
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    # Executa o aplicativo Flask no loop de eventos existente
    from threading import Thread

    def run_flask():
        app.run(use_reloader=False)

    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass