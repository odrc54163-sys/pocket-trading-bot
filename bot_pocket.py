from datetime import datetime
import os
from threading import Thread
import pytz
from flask import Flask
import telebot

# Configura tu token de Telegram aquí
TOKEN = '8836340643:AAELtdRqcjPzL60PG1JBZy32TwWy0cVMF5Q'
CHAT_ID = '2140660100'
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
def enviar_senal(chat_id, activo, direccion, tiempo):
  tz = pytz.timezone('America/Caracas')
  ahora = datetime.now(tz)

  # Hora sin ceros a la izquierda (ej: 2:32 PM)
  hora_actual = f"{ahora.strftime('%I').lstrip('0')}:{ahora.strftime('%M %p')}"

  if direccion.lower() == 'subida':
    emoji_dir = '🟢'
    accion = '¡APUESTA A LA SUBIDA!'
  else:
    emoji_dir = '🔴'
    accion = '¡APUESTA A LA BAJA!'

  mensaje = (
      f'🚨 📉📈 🚨\n\n'
      f'{emoji_dir} **{accion}** {emoji_dir}\n\n'
      f'💱 **Moneda:** {activo.upper()}\n'
      f'⏱️ **Tiempo / Expiración:** {tiempo}\n'
      f'⏰ **Hora de envío:** {hora_actual}'
  )

  bot.send_message(chat_id, mensaje, parse_mode='Markdown')


# 3. Comandos de prueba en Telegram
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  bot.reply_to(
      message,
      '¡Hola! El bot de trading está en línea.\nUsa el formato: `/senal EURUSD subida 1M` para probar.',
      parse_mode='Markdown',
  )


@bot.message_handler(commands=['senal'])
def handle_senal(message):
  try:
    partes = message.text.split()
    activo = partes[1]  # Ejemplo: EURUSD
    direccion = partes[2]  # Ejemplo: subida o baja
    tiempo = partes[3]  # Ejemplo: 1M o 5M
    enviar_senal(message.chat.id, activo, direccion, tiempo)
  except Exception as e:
    bot.reply_to(
        message,
        '❌ **Uso incorrecto.**\nFormato correcto: `/senal EURUSD subida 1M`',
        parse_mode='Markdown',
    )


# 4. Punto de entrada principal
if __name__ == '__main__':
  # Inicia el servidor web en segundo plano para abrir el puerto en Render
  keep_alive()

  # Limpia webhooks pendientes para evitar conflictos de Telegram
  bot.remove_webhook()

  # Inicia el bot de Telegram en bucle continuo
  print('Iniciando bot de Telegram y servidor web...')
  bot.infinity_polling()
