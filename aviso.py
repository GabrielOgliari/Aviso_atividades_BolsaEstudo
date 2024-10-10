import requests
from telegram import Bot
import time
import json
import os
import asyncio

# Configurações do Telegram
BOT_TOKEN = '7514578178:AAGXKsSqf8bY2GUhG5F32XADph_MZ5CJrzc'
CHAT_ID = '5782098350'

# URL a ser monitorada
URL = 'https://eventos.unochapeco.edu.br/eventos/'
URL = 'https://eventos.unochapeco.edu.br/Auxiliar/RetornarListaEventoWhiteLabel'

# Payload JSON para a requisição POST
payload = {
    "model": "{\"cidade\":null,\"filtroCampoTexto\":\"PUG\",\"ano\":null,\"unidade\":null,\"formatoEvento\":\"\"}"
}

def gravar_log(id):
    with open('log.txt', 'a') as log_file:
        log_file.write(f'{id}\n')

# Função para verificar a presença do texto específico nos resultados da resposta
def verificar_site():
    response = requests.post(URL, json=payload)
    if response.status_code == 200:
        response_text = response.text

        response_json = json.loads(response_text)
        objects = response_json['Object']

        for obj in objects:
            id = obj['id']
            if "PUG" in obj['titulo']:
                if os.path.exists('log.txt'):
                    with open('log.txt', 'r') as log_file:
                        log = log_file.read()
                    if str(id) in log:
                        continue
                gravar_log(id)
                return obj['url']

    # return None

# Função para enviar uma mensagem no Telegram
async def send_message_to_telegram(text):
    try:
        bot = Bot(token='8069837006:AAFhgqqv0SNkzUDLgBEgpRKFAy_Ev5WR59A')
        await bot.send_message(chat_id='-4503091244', text=text)
        return True
    except Exception as e:
        print(f'Erro ao enviar mensagem para o telegram: {e}')

async def main():
    while True:
        url = verificar_site()
        if url:
            link = f'https://eventos.unochapeco.edu.br/{url}'
            await send_message_to_telegram(f'nova atividade encontrada:\n\n{link}')
        time.sleep(300)  # Espera 5 minutos antes de verificar novamente


if __name__ == '__main__':
    asyncio.run(main())