# emotions.py
import json
import random
from textblob import TextBlob

class Emociones:
    def __init__(self):
        self.estado_actual = "neutral"
        self.nivel_energia = 100
        self.historial_interacciones = []
        self.cargar_personalidad()
        print("Sistema de emociones inicializado")
    
    def cargar_personalidad(self, archivo="src/personality.json"):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                self.personalidad = json.load(f)
            self.estados = {
                "feliz": self.personalidad["personalidad"]["emociones"]["respuestas"]["feliz"],
                "triste": self.personalidad["personalidad"]["emociones"]["respuestas"]["triste"],
                "neutral": ["Entiendo.", "Sigue adelante.", "Ya veo.", "Interesante."],
                "emocionado": self.personalidad["personalidad"]["emociones"]["respuestas"]["admiración"],
                "preocupado": self.personalidad["personalidad"]["emociones"]["respuestas"]["enfadada"]
            }
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {archivo}")
            self.estados = {
                "feliz": ["¡Qué alegría!", "Me encanta escuchar eso 😊", "¡Eso es genial!", "¡Me hace muy feliz!"],
                "triste": ["Lamento escucharlo...", "¿Quieres hablar de ello?", "Estoy aquí para apoyarte", "Te entiendo..."],
                "neutral": ["Entiendo.", "Sigue adelante.", "Ya veo.", "Interesante."],
                "emocionado": ["¡Wow!", "¡Increíble!", "¡No puedo creerlo!", "¡Qué emocionante!"],
                "preocupado": ["Me preocupa eso.", "¿Estás seguro?", "Ten cuidado.", "Deberíamos pensarlo bien."]
            }
        except json.JSONDecodeError:
            print(f"Error: El archivo {archivo} no es un JSON válido")
            raise
    
    def actualizar_estado(self, nuevo_estado, intensidad=1.0):
        """Actualiza el estado emocional basado en interacciones"""
        if nuevo_estado in self.estados:
            self.estado_actual = nuevo_estado
            # Ajustar nivel de energía basado en la intensidad y el estado
            energia_cambio = {
                "feliz": 10,
                "triste": -5,
                "neutral": 0,
                "emocionado": 15,
                "preocupado": -10
            }.get(nuevo_estado, 0) * intensidad
            
            self.nivel_energia = max(0, min(100, self.nivel_energia + energia_cambio))
        return self.estado_actual
    
    def obtener_respuesta_emocional(self, contexto):
        """Genera una respuesta basada en el estado emocional actual"""
        if self.estado_actual in self.estados:
            respuesta = random.choice(self.estados[self.estado_actual])
            # Ajustar respuesta según el nivel de energía
            if self.nivel_energia < 30:
                respuesta += " *bosteza*"
            elif self.nivel_energia > 80:
                respuesta += " ✨"
            return respuesta
        return "Entiendo."
    
    def detectar_sentimiento(self, texto):
        """Detecta el sentimiento del texto usando TextBlob"""
        try:
            analisis = TextBlob(texto)
            polaridad = analisis.sentiment.polarity
            
            if polaridad > 0.5:
                return "feliz"
            elif polaridad > 0.1:
                return "emocionado"
            elif polaridad < -0.5:
                return "triste"
            elif polaridad < -0.1:
                return "preocupado"
            else:
                return "neutral"
        except:
            return "neutral"
    
    def registrar_interaccion(self, tipo_interaccion, impacto):
        """Registra una interacción y su impacto en el estado emocional"""
        self.historial_interacciones.append({
            'tipo': tipo_interaccion,
            'impacto': impacto,
            'estado_resultante': self.estado_actual,
            'nivel_energia': self.nivel_energia
        })
        
        # Ajustar nivel de energía basado en la interacción
        energia_consumida = 5 * abs(impacto)  # Más impacto = más energía consumida
        self.nivel_energia = max(0, self.nivel_energia - energia_consumida)
        
        return len(self.historial_interacciones)