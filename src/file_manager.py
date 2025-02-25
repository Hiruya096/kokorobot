# file_manager.py
from datetime import datetime
import requests
import discord
import os
import zipfile
import math
import sqlite3

class FileManager:
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1343830979592196158  # ID del canal para archivos
        self.max_fragment_size = 50 * 1024 * 1024  # 50MB en bytes
        # Inicializar la base de datos
        self.conn = sqlite3.connect("almacenamiento.db")
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        """Inicializa la tabla de fragmentos en la base de datos."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS fragmentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            descripcion TEXT,
            fecha_creacion TEXT,
            url TEXT
        )
        """)
        self.conn.commit()

    def guardar_fragmento(self, nombre, descripcion, url):
        """Guarda información del fragmento en la base de datos."""
        self.cursor.execute("""
        INSERT INTO fragmentos (nombre, descripcion, fecha_creacion, url)
        VALUES (?, ?, datetime('now'), ?)
        """, (nombre, descripcion, url))
        self.conn.commit()

    def obtener_fragmentos(self):
        """Recupera todos los fragmentos almacenados."""
        self.cursor.execute("SELECT * FROM fragmentos")
        return self.cursor.fetchall()

    def comprimir_archivo(self, ruta_archivo, ruta_comprimida=None):
        """Comprime un archivo usando ZIP."""
        try:
            if not ruta_comprimida:
                ruta_comprimida = f"{ruta_archivo}.zip"

            with zipfile.ZipFile(ruta_comprimida, "w", zipfile.ZIP_DEFLATED) as archivo_zip:
                archivo_zip.write(ruta_archivo, os.path.basename(ruta_archivo))
            print(f"Archivo comprimido: {ruta_comprimida}")
            return ruta_comprimida
        except Exception as e:
            print(f"Error al comprimir archivo: {str(e)}")
            return None

    def fragmentar_archivo(self, ruta_archivo):
        """Fragmenta un archivo en partes de 50MB."""
        try:
            if not os.path.exists(ruta_archivo):
                print(f"Archivo no encontrado: {ruta_archivo}")
                return []

            tamano = os.path.getsize(ruta_archivo)
            if tamano <= self.max_fragment_size:
                return [ruta_archivo]

            num_fragmentos = math.ceil(tamano / self.max_fragment_size)
            fragmentos = []
            nombre_base = os.path.splitext(ruta_archivo)[0]

            with open(ruta_archivo, 'rb') as f:
                for i in range(num_fragmentos):
                    nombre_fragmento = f"{nombre_base}_part{i+1}.zip"
                    contenido = f.read(self.max_fragment_size)
                    with open(nombre_fragmento, 'wb') as fragment:
                        fragment.write(contenido)
                    fragmentos.append(nombre_fragmento)

            print(f"Archivo fragmentado en {len(fragmentos)} partes")
            return fragmentos
        except Exception as e:
            print(f"Error al fragmentar archivo: {str(e)}")
            return []

    async def subir_archivo(self, ruta_archivo, descripcion=""):
        """Sube un archivo al canal especificado, comprimiendo y fragmentando si es necesario."""
        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                print("Canal no encontrado.")
                return None

            if not os.path.exists(ruta_archivo):
                print(f"Archivo no encontrado: {ruta_archivo}")
                return None

            # Comprimir el archivo
            ruta_comprimida = self.comprimir_archivo(ruta_archivo)
            if not ruta_comprimida:
                return None

            # Fragmentar si es necesario
            fragmentos = self.fragmentar_archivo(ruta_comprimida)
            urls = []

            for fragmento in fragmentos:
                async with open(fragmento, "rb") as archivo:
                    mensaje = await channel.send(
                        file=discord.File(archivo, filename=os.path.basename(fragmento))
                    )
                    url = mensaje.attachments[0].url
                    urls.append(url)
                    # Guardar información del fragmento en la base de datos
                    self.guardar_fragmento(
                        os.path.basename(fragmento),
                        descripcion,
                        url
                    )

            # Limpiar archivos temporales
            if ruta_comprimida != ruta_archivo:
                os.remove(ruta_comprimida)
            for fragmento in fragmentos:
                if fragmento != ruta_archivo:
                    os.remove(fragmento)

            print(f"Archivo subido en {len(urls)} partes")
            return urls[0] if len(urls) == 1 else urls

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

    def __del__(self):
        """Cierra la conexión a la base de datos cuando se destruye el objeto."""
        if hasattr(self, 'conn'):
            self.conn.close()