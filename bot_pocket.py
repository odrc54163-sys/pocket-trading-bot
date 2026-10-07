import time
from datetime import datetime
import telebot

# --- TUS DATOS ---
TOKEN = "8836340643:AAEq-FgcW6JZU-3-XouhUzBFjleGB-X8Sj8"
CHAT_ID = "2140660100"

bot = telebot.TeleBot(TOKEN)

print("--- BOT DE SEÑALES POCKET OPTION ACTIVO ---")

while True:
    ahora = datetime.now()
    minuto = ahora.minute
    segundo = ahora.second

    # Detecta el momento exacto (3 minutos antes de un ciclo de 5 minutos)
    if (minuto + 3) % 5 == 0 and segundo == 0:
        
        # --- MENSAJE 1: Aviso de preparación (3 minutos antes) ---
        mensaje_preparacion = (
            "⚠️ **¡ATENCIÓN!** ⚠️\n"
            "Mantente pendiente, en 3 minutos te pasaré la señal exacta para operar en Pocket Option."
        )
        
        bot.send_message(CHAT_ID, mensaje_preparacion, parse_mode="Markdown")
        print("[1] Aviso de preparación enviado a Telegram.")
        
        # Esperamos exactamente 2 minutos con 50 segundos (170 segundos)
        time.sleep(170)
        
        # --- MENSAJE 2: La señal exacta limpia con emojis dinámicos ---
        activo = "EUR/USD"
        momento_entrada = "Segundo 30" 
        
        # Puedes cambiar esto a "SUBIDA" o "BAJADA" según lo que analice tu lógica
        accion = "APUESTA A LA SUBIDA"  # O "APUESTA A LA BAJA"
        
        # Asignamos el emoji según la dirección
        if "SUBIDA" in accion.upper():
            icono = "🟢"
        else:
            icono = "🔴"
        
        mensaje_final = (
            f"🚨 **SEÑAL DE OPCIONES BINARIAS** 🚨\n"
            f"🪙 Activo: {activo}\n"
            f"⏱️ Momento de entrada: {momento_entrada}\n"
            f"{icono} Acción: {accion}"
        )
        
        bot.send_message(CHAT_ID, mensaje_final, parse_mode="Markdown")
        print("[2] Señal exacta enviada a Telegram.")
        
        # Pausa para dejar pasar el minuto actual
        time.sleep(10)

    # El bot revisa el reloj cada segundo
    time.sleep(1)
