# api_handler.py
import requests
from gtts import gTTS
import os
import discord
import json
import asyncio
from typing import Optional, Dict, Any

class APIHandler:
    def __init__(self, api_key: str, discord_token: Optional[str] = None, discord_channel_id: Optional[int] = None):
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/",
            "Content-Type": "application/json"
        }
        self.discord_token = discord_token
        self.discord_channel_id = discord_channel_id
        self.discord_client = None
        if discord_token and discord_channel_id:
            self.setup_discord()
        print("API Handler inicializado")
    
    def setup_discord(self):
        """Configura el cliente de Discord"""
        intents = discord.Intents.default()
        intents.message_content = True
        self.discord_client = discord.Client(intents=intents)

    async def get_discord_response(self, mensaje: str) -> str:
        """Obtiene una respuesta desde Discord como fallback"""
        if not self.discord_client or not self.discord_channel_id:
            return "Sistema de respaldo no disponible."
        
        try:
            channel = self.discord_client.get_channel(self.discord_channel_id)
            if not channel:
                return "Canal de Discord no encontrado."

            # Buscar respuestas almacenadas
            async for message in channel.history(limit=100):
                if message.content.startswith(mensaje[:50]):
                    return message.content.split('||')[1] if '||' in message.content else message.content
            return "No se encontró una respuesta adecuada en el respaldo."
        except Exception as e:
            print(f"Error al obtener respuesta de Discord: {e}")
            return "Error al acceder al sistema de respaldo."

    def procesar_mensaje(self, mensaje: str) -> str:
        """Procesa un mensaje usando la API de OpenRouter con fallback a Discord"""
        try:
            payload = {
                "model": "mistralai/mistral-small-24b-instruct-2501",
                "messages": [{"role": "user", "content": mensaje}],
                "max_tokens": 200
            }
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            respuesta = data['choices'][0]['message']['content'].strip()
            
            # Almacenar la respuesta en Discord si está disponible
            if self.discord_client and self.discord_channel_id:
                asyncio.create_task(self.store_response(mensaje, respuesta))
            
            return respuesta
        except Exception as e:
            print(f"Error al procesar mensaje con OpenRouter: {e}")
            # Intentar obtener respuesta de Discord
            if self.discord_client:
                return asyncio.run(self.get_discord_response(mensaje))
            return "Lo siento, hubo un error al procesar tu mensaje."
    
    def obtener_respuesta(self, contexto):
        """Obtiene una respuesta basada en el contexto"""
        prompt = f"Contexto: {contexto}\nPor favor, genera una respuesta apropiada."
        return self.procesar_mensaje(prompt)
    
    def analizar_sentimiento(self, texto):
        """Analiza el sentimiento del texto usando la API"""
        try:
            prompt = f"Analiza el sentimiento del siguiente texto y clasifícalo como feliz, triste, neutral, emocionado o preocupado: {texto}"
            respuesta = self.procesar_mensaje(prompt)
            
            # Mapear la respuesta a un formato de sentimiento
            sentimientos = {
                "feliz": 0.8,
                "triste": 0.2,
                "neutral": 0.5,
                "emocionado": 0.9,
                "preocupado": 0.3
            }
            
            for sentimiento, confianza in sentimientos.items():
                if sentimiento.lower() in respuesta.lower():
                    return {"sentimiento": sentimiento, "confianza": confianza}
            
            return {"sentimiento": "neutral", "confianza": 0.5}
        except Exception as e:
            print(f"Error al analizar sentimiento: {e}")
            return {"sentimiento": "neutral", "confianza": 0.5}
    
    def texto_a_voz(self, texto: str, archivo_salida: str = "respuesta.mp3") -> bool:
        """Convierte texto a voz usando gTTS"""
        try:
            tts = gTTS(text=texto, lang='es')
            tts.save(archivo_salida)
            return True
        except Exception as e:
            print(f"Error al convertir texto a voz: {e}")
            return False
            
    async def store_response(self, pregunta: str, respuesta: str) -> None:
        """Almacena la pregunta y respuesta en Discord para futuros usos"""
        if not self.discord_client or not self.discord_channel_id:
            return
            
        try:
            channel = self.discord_client.get_channel(self.discord_channel_id)
            if channel:
                await channel.send(f"{pregunta}||{respuesta}")
        except Exception as e:
            print(f"Error al almacenar respuesta en Discord: {e}")