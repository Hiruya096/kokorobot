# file_manager.py
from datetime import datetime
import requests
import discord
import os

class FileManager:
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1343830979592196158  # ID del canal para archivos

    async def subir_archivo(self, ruta_archivo):
        """Sube un archivo al canal especificado."""
        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                print("Canal no encontrado.")
                return None

            if not os.path.exists(ruta_archivo):
                print(f"Archivo no encontrado: {ruta_archivo}")
                return None

            async with open(ruta_archivo, "rb") as archivo:
                mensaje = await channel.send(file=discord.File(archivo))
                url = mensaje.attachments[0].url
                print(f"Archivo subido: {url}")
                return url

        except Exception as e:
            print(f"Error al subir archivo: {str(e)}")
            return None

    def descargar_archivo(self, url, destino):
        """Descarga un archivo desde una URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()

            os.makedirs(os.path.dirname(destino), exist_ok=True)
            
            with open(destino, "wb") as archivo:
                archivo.write(response.content)
            print(f"Archivo descargado: {destino}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error al descargar archivo: {str(e)}")
            return False
        except IOError as e:
            print(f"Error al guardar archivo: {str(e)}")
            return False

    async def limpiar_canal(self, dias=7):
        """Elimina mensajes antiguos del canal."""
        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                print("Canal no encontrado.")
                return False

            async for mensaje in channel.history(limit=None):
                if (datetime.now() - mensaje.created_at).days > dias:
                    await mensaje.delete()
                    print(f"Mensaje eliminado: {mensaje.id}")
            return True

        except Exception as e:
            print(f"Error al limpiar canal: {str(e)}")
            return False

    def set_channel_id(self, channel_id):
        """Actualiza el ID del canal para archivos."""
        self.channel_id = channel_id