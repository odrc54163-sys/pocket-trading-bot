from datetime import datetime
import os
from threading import Thread
import time
import pytz
from flask import Flask
import pandas as pd
import telebot
import yfinance as yf  # Librería para obtener datos financieros reales

# Configura tu token y chat ID
TOKEN = '8836340643:AAGDEy9Q-4KRpjPuyiiFLtsQcmdZPlFI2PY'
CHAT_ID = '2140660100'
bot = telebot.TeleBot(TOKEN)

# 1. Configurar servidor web para Render y UptimeRobot
app = Flask('')


@app.route('/')
def home():
  return '¡El bot de análisis de mercado está activo!'


def run():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


def keep_alive():
  t = Thread(target=run)
  t.start()


# 2. Función para enviar la señal con tu formato exacto
def enviar_senal(chat_id, activo, direccion, tiempo):
  tz = pytz.timezone('America/Caracas')
  ahora = datetime.now(tz)
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


# 3. Función para calcular el RSI (Indicador Técnico)
def calcular_rsi(data, window=14):
  delta = data['Close'].diff()
  gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
  loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
  rs = gain / loss
  rsi = 100 - (100 / (1 + rs))
  return rsi


# 4. Bucle de análisis de mercado en tiempo real
def analizar_mercado():
  # Activo que vamos a vigilar en el mercado global (compatible con Pocket Option)
  activo = 'EURUSD=X'
  nombre_mostrar = 'EURUSD'

  # Espera un momento al encender para estabilizar el servidor
  time.sleep(15)

  while True:
    try:
      # Descarga datos recientes de las últimas horas (velas de 1 minuto o 5 minutos)
      df = yf.download(
          activo, period='1d', interval='5m', progress=False
      )

      if not df.empty and len(df) > 20:
        # Calcular RSI
        df['RSI'] = calcular_rsi(df)
        ultimo_rsi = df['RSI'].iloc[-1]

        print(f'Analizando {nombre_mostrar} - RSI actual: {ultimo_rsi:.2f}')

        # Regla de estrategia:
        # Si RSI < 30 (Sobreventa -> El precio cayó mucho, probable subida)
        if ultimo_rsi < 30:
          enviar_senal(CHAT_ID, nombre_mostrar, 'subida', '5M')
          # Esperar 15 minutos para no repetir señal seguida en el mismo activo
          time.sleep(900)

        # Si RSI > 70 (Sobrecompra -> El precio subió mucho, probable baja)
        elif ultimo_rsi > 70:
          enviar_senal(CHAT_ID, nombre_mostrar, 'baja', '5M')
          time.sleep(900)

      # Revisa el mercado cada 60 segundos
      time.sleep(60)

    except Exception as e:
      print(f'Error en el análisis de mercado: {e}')
      time.sleep(60)


# 5. Punto de entrada principal
if __name__ == '__main__':
  keep_alive()

  # Iniciar el hilo de análisis técnico en segundo plano
  hilo_analisis = Thread(target=analizar_mercado)
  hilo_analisis.daemon = True
  hilo_analisis.start()

  bot.remove_webhook()
  print('Iniciando bot analista de mercado y servidor web...')
  bot.infinity_polling()
