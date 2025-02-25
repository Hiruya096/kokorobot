# discord_bot.py
import discord
from discord.ext import commands

class DiscordBot:
    def __init__(self, api_handler, emociones):
        self.api_handler = api_handler
        self.emociones = emociones
        self.bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
        print("Bot de Discord inicializado")
        
        # Registrar eventos
        @self.bot.event
        async def on_ready():
            print(f"Bot conectado como {self.bot.user}")
        
        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return
                
            # Procesar el mensaje y obtener respuesta
            respuesta = self.api_handler.procesar_mensaje(message.content)
            sentimiento = self.api_handler.analizar_sentimiento(message.content)
            
            # Actualizar estado emocional
            self.emociones.actualizar_estado(sentimiento['sentimiento'])
            respuesta_emocional = self.emociones.obtener_respuesta_emocional(message.content)
            
            # Registrar la interacción
            self.emociones.registrar_interaccion('mensaje', sentimiento['confianza'])
            
            # Enviar respuestas
            await message.channel.send(respuesta)  # Enviar respuesta del API
            await message.channel.send(respuesta_emocional)  # Enviar respuesta emocional
            
            await self.bot.process_commands(message)
    
    def iniciar(self, token):
        """Inicia el bot de Discord"""
        self.bot.run(token)