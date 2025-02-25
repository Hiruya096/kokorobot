# api_handler.py
import requests
from gtts import gTTS
import os

class APIHandler:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/",
            "Content-Type": "application/json"
        }
        print("API Handler inicializado")
    
    def procesar_mensaje(self, mensaje):
        """Procesa un mensaje usando la API de OpenRouter"""
        try:
            payload = {
                "model": "mistralai/mistral-small-24b-instruct-2501",
                "messages": [{"role": "user", "content": mensaje}],
                "max_tokens": 200
            }
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Error al procesar mensaje: {e}")
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
    
    def texto_a_voz(self, texto, archivo_salida="respuesta.mp3"):
        """Convierte texto a voz usando gTTS"""
        try:
            tts = gTTS(text=texto, lang='es')
            tts.save(archivo_salida)
            return True
        except Exception as e:
            print(f"Error al convertir texto a voz: {e}")
            return False