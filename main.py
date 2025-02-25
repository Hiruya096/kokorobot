# main.py
from dotenv import load_dotenv
import os
import threading
from src.api_handler import APIHandler
from src.discord_bot import DiscordBot
from src.emotions import Emociones
from src.web_interface import iniciar_web

# Cargar variables de entorno
load_dotenv()

# Obtener variables de entorno
API_KEY = os.getenv('OPENROUTER_API_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

def iniciar_kokoro():
    print("Iniciando Kokoro Hikari...")
    # Inicializar módulos
    api_handler = APIHandler(API_KEY)
    personalidad = Emociones()  # Carga la personalidad y emociones desde el archivo
    discord_bot = DiscordBot(api_handler, personalidad)
    
    # Iniciar bot de Discord
    discord_bot.iniciar(DISCORD_TOKEN)
    
    # Iniciar interfaz web en un hilo separado
    web_thread = threading.Thread(target=iniciar_web)
    web_thread.daemon = True  # El hilo se cerrará cuando el programa principal termine
    web_thread.start()

if __name__ == "__main__":
    iniciar_kokoro()