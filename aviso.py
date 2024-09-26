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
def verificar_site():
    response = requests.post(URL, json=payload)
    if response.status_code == 200:
        response_text = response.text
        notified_responses = load_notified_responses()

        # Verifica se a resposta já foi notificada
        if response_text not in notified_responses:
            if "PUG" in response_text:  # Verifica se o texto "PUG" está na resposta
                save_notified_response(response_text)
                return response_text  # Retorna o texto completo encontrado
    return None

# Função para enviar uma mensagem no Telegram
async def send_message_to_telegram(text):
    print(text)
    try:
        bot = Bot(token='8069837006:AAFhgqqv0SNkzUDLgBEgpRKFAy_Ev5WR59A')
        await bot.send_message(chat_id='5782098350', text='nova atividade')
        return True
    except Exception as e:
        print(f'Erro ao enviar mensagem para o telegram: {e}')

async def main():
    while True:
        texto_encontrado = verificar_site()
        if texto_encontrado:
            await send_message_to_telegram(f'O texto "PUG" foi encontrado no site! Texto completo:\n\n{texto_encontrado}')
        time.sleep(5)  # Espera 5 minutos antes de verificar novamente

if __name__ == '__main__':
    asyncio.run(main())