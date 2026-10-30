from datetime import datetime, timedelta
import os
from threading import Thread
import time
import pytz
from flask import Flask
import pandas as pd
import telebot
import yfinance as yf

TOKEN = '8836340643:AAELtdRqcjPzL60PG1JBZy32TwWy0cVMF5Q'
CHAT_ID = '2140660100'
bot = telebot.TeleBot(TOKEN)

# 1. Servidor web para mantener el bot activo en Render
app = Flask('')


@app.route('/')
def home():
  return '¡El bot de señales multimoneda está activo!'


def run():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


def keep_alive():
  t = Thread(target=run)
  t.start()


# 2. Función con el formato exacto del mensaje (limpio y directo)
def enviar_senal(chat_id, activo, direccion, tiempo):
  tz = pytz.timezone('America/Caracas')
  ahora = datetime.now(tz)

  # Calcular el siguiente minuto múltiplo de 5 para la vela exacta
  minuto_actual = ahora.minute
  resto = minuto_actual % 5
  minutos_a_sumar = 5 - resto if resto != 0 else 5

  siguiente_tiempo = ahora.replace(
      second=0, microsecond=0
  ) + timedelta(minutes=minutos_a_sumar)
  hora_entrada = f"{siguiente_tiempo.strftime('%I').lstrip('0')}:{siguiente_tiempo.strftime('%M:%S %p')}"
  hora_envio = f"{ahora.strftime('%I').lstrip('0')}:{ahora.strftime('%M %p')}"

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
      f'🎯 **Entrada exacta:** A las **{hora_entrada}** (Segundo 00)\n'
      f'⏰ **Hora de envío:** {hora_envio}'
  )

  bot.send_message(chat_id, mensaje, parse_mode='Markdown')


# 3. Cálculo matemático del RSI
def calcular_rsi(data, window=14):
  delta = data['Close'].diff()
  gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
  loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
  rs = gain / loss
  rsi = 100 - (100 / (1 + rs))
  return rsi


# 4. Analizador que recorre todas las monedas de la lista de forma rotativa
def analizar_mercado():
  # Aquí tienes todas las principales monedas listas para ser escaneadas
  pares = {
      'EURUSD=X': 'EURUSD',
      'GBPUSD=X': 'GBPUSD',
      'USDJPY=X': 'USDJPY',
      'AUDUSD=X': 'AUDUSD',
      'USDCAD=X': 'USDCAD',
      'EURJPY=X': 'EURJPY',
      'GBPJPY=X': 'GBPJPY',
  }

  time.sleep(10)

  while True:
    for ticker, nombre in pares.items():
      try:
        df = yf.download(ticker, period='1d', interval='5m', progress=False)

        if not df.empty and len(df) > 20:
          df['RSI'] = calcular_rsi(df)
          ultimo_rsi = df['RSI'].iloc[-1]

          print(f'Revisando {nombre} - RSI: {ultimo_rsi:.2f}')

          if ultimo_rsi < 30:
            enviar_senal(CHAT_ID, nombre, 'subida', '5M')
            time.sleep(300)  # Pausa de 5 min para este par tras dar señal

          elif ultimo_rsi > 70:
            enviar_senal(CHAT_ID, nombre, 'baja', '5M')
            time.sleep(300)

        # Pausa corta entre cada moneda para evitar bloqueos en las peticiones
        time.sleep(6)

      except Exception as e:
        print(f'Error en {nombre}: {e}')
        time.sleep(5)

    # Pausa antes de volver a empezar la ronda con todas las monedas
    time.sleep(15)


# 5. Inicio del programa principal
if __name__ == '__main__':
  keep_alive()

  hilo_analisis = Thread(target=analizar_mercado)
  hilo_analisis.daemon = True
  hilo_analisis.start()

  bot.remove_webhook()
  print('Iniciando bot con todas las monedas y formato limpio...')
  bot.infinity_polling()
