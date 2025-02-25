# Kokoro Hikari Bot

Un bot de IA llamado Kokoro Hikari con capacidades de gestión de archivos y emociones.

## Características

- Procesamiento de mensajes con IA
- Sistema de emociones y personalidad
- Gestión de archivos en Discord
  - Subida de archivos
  - Descarga de archivos
  - Limpieza automática del canal de archivos
- Interfaz web para monitoreo

## Estructura del Proyecto

```
/src
  ├── api_handler.py    # Manejo de API de IA
  ├── discord_bot.py    # Cliente principal de Discord
  ├── emotions.py       # Sistema de emociones
  ├── file_manager.py   # Gestión de archivos
  ├── keep_alive.py     # Mantener el bot en línea
  ├── web_interface.py  # Interfaz web
  └── templates/        # Plantillas HTML
```

## Configuración

1. Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
   ```
   OPENROUTER_API_KEY=tu_api_key
   DISCORD_BOT_TOKEN=tu_token_de_discord
   ```

2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Ejecuta el bot:
   ```
   python main.py
   ```