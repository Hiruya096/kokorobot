# web_interface.py
from flask import Flask, render_template, jsonify
from datetime import datetime
from threading import Lock

app = Flask(__name__)
status_lock = Lock()

# Estado global del bot
bot_status = {
    "start_time": datetime.now(),
    "messages_processed": 0,
    "current_emotion": "neutral",
    "energy_level": 100,
    "is_running": True
}

@app.route('/')
def home():
    """Página principal del dashboard"""
    return render_template('dashboard.html', status=bot_status)

@app.route('/api/status')
def get_status():
    """Endpoint API para obtener el estado actual del bot"""
    return jsonify({
        "uptime": str(datetime.now() - bot_status["start_time"]),
        "messages": bot_status["messages_processed"],
        "emotion": bot_status["current_emotion"],
        "energy": bot_status["energy_level"]
    })

def actualizar_estado(messages=None, emotion=None, energy=None, running=None):
    """Actualiza el estado del bot de manera thread-safe"""
    with status_lock:
        if messages is not None:
            bot_status["messages_processed"] = messages
        if emotion is not None:
            bot_status["current_emotion"] = emotion
        if energy is not None:
            bot_status["energy_level"] = energy
        if running is not None:
            bot_status["is_running"] = running

def iniciar_web(host='0.0.0.0', port=5000):
    """Inicia la interfaz web"""
    print("Iniciando interfaz web en http://{}:{}".format(host, port))
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    iniciar_web()