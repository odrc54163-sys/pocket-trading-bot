import os
from datetime import datetime
from threading import Thread
import pytz
from flask import Flask
import telebot

# Configura tu token de Telegram aquí
TOKEN = '2140660100'
bot = telebot.TeleBot(TOKEN)

# 1. Configurar mini servidor web con Flask para Render y UptimeRobot
app = Flask('')


@app.route('/')
def home():
  return '¡El bot de señales está activo y funcionando!'


def run():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


def keep_alive():
  t = Thread(target=run)
  t.start()


# 2. Función para formatear y enviar la señal con la estructura solicitada
def enviar_senal(chat_id, direccion, tiempo):
  # Obtener la hora actual de Venezuela (o ajusta la zona horaria que prefieras)
  tz = pytz.timezone('America/Caracas')
  hora_actual = datetime.now(tz).strftime('%I:%M %p')

  # Definir emoji y texto según si es a la baja o a la subida
  if direccion.lower() == 'subida':
    emoji_dir = '🟢'
    accion = '¡Apuesta a la Subida grande!'
  else:
    emoji_dir = '🔴'
    accion = '¡Apuesta a la Baja grande!'

  # Estructura del mensaje sin "Atención papá", solo emojis y datos
  mensaje = (
      f'🚨 📉📈 🚨\n\n'
      f'{emoji_dir} **{accion}** {emoji_dir}\n'
      f'⏱️ **Tiempo:** {tiempo}\n'
      f'⏰ **Hora:** {hora_actual}'
  )

  bot.send_message(chat_id, mensaje, parse_mode='Markdown')


# 3. Comandos de prueba en Telegram
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      '¡Hola! El bot de trading está en línea. Usa /senal subida 1M o'
      ' /senal baja 5M para probar.',
  )


@bot.message_handler(commands=['senal'])
def handle_senal(message):
  try:
    # Ejemplo de uso: /senal subida 1M o /senal baja 5M
    partes = message.text.split()
    direccion = partes[1]  # subida o baja
    tiempo = partes[2]  # ej: 1M, 5M
    enviar_senal(message.chat.id, direccion, tiempo)
  except Exception as e:
    bot.reply_to(
        message,
        'Uso correcto: `/senal subida 1M` o `/senal baja 5M`',
        parse_mode='Markdown',
    )


# 4. Punto de entrada principal
if __name__ == '__main__':
  # Inicia el servidor web en segundo plano para abrir el puerto en Render
  keep_alive()

  # Inicia el bot de Telegram en bucle continuo
  print('Iniciando bot de Telegram y servidor web...')
  bot.infinity_polling()
