# X3 Elite v4.1 - Asistente de Voz Personal

Este proyecto implementa un asistente de voz personal llamado X3 Elite, versión 4.1, desarrollado en Python. Combina capacidades de reconocimiento y síntesis de voz, procesamiento de lenguaje natural (NLU), scraping web, monitoreo del sistema y una interfaz de usuario web (HUD) interactiva.

## Características Principales

*   **Reconocimiento de Voz:** Utiliza Google Speech Recognition para transcribir comandos de voz.
*   **Síntesis de Voz:** Genera respuestas habladas usando Edge TTS.
*   **Procesamiento de Lenguaje Natural (NLU):** Clasifica intenciones de usuario mediante un modelo SVC entrenado con `scikit-learn` y `TfidfVectorizer`.
*   **Scraping Web:** Capacidad para diseccionar URLs y extraer contenido web utilizando `requests` y `BeautifulSoup`.
*   **Monitoreo del Sistema:** Proporciona información en tiempo real sobre el uso de CPU y RAM con `psutil`.
*   **Memoria Segura:** Almacena datos en una base de datos SQLite (`x3_memory.db`) con cifrado AES-128 (`cryptography.fernet`) para proteger información sensible.
*   **Interfaz de Usuario Web (HUD):** Incluye un servidor HTTP y WebSocket para mostrar un panel de control interactivo en el navegador, utilizando Three.js para visualizaciones y actualizando datos del sistema en tiempo real.

## Dependencias

El script `x3.py` requiere las siguientes librerías de Python. El script intenta instalarlas automáticamente si no están presentes:

*   `speech_recognition`
*   `edge-tts`
*   `requests`
*   `cryptography`
*   `websockets`
*   `psutil`
*   `scikit-learn`
*   `beautifulsoup4`

## Uso

Para ejecutar el asistente X3 Elite, simplemente ejecuta el script `x3.py`:

```bash
python3 x3.py
```

Una vez iniciado, el asistente escuchará el micrófono. Cuando detecte la palabra de activación configurada (por defecto, "x3"), procesará el comando de voz subsiguiente. La interfaz HUD estará disponible en `http://localhost:8080`.

## Estructura del Código

El script está organizado en varias secciones clave:

*   **Gestión de Dependencias:** Verifica e instala automáticamente las librerías necesarias.
*   **Configuración JARVIS 2026:** Define constantes como la palabra de activación, nombre de usuario, rutas de archivos y puertos de servicio.
*   **Seguridad AES-128:** Implementa funciones para cifrar y descifrar datos utilizando `Fernet` de la librería `cryptography`, asegurando la persistencia de la memoria.
*   **MemoryVault:** Una clase para interactuar con la base de datos SQLite, permitiendo guardar y recuperar información cifrada.
*   **Inteligencia NLU SVC:** La clase `OmniNLU` entrena un clasificador `SVC` para predecir la intención del usuario a partir de comandos de texto.
*   **Núcleo X3 Élite:** La clase `X3EliteV4` es el corazón del asistente, gestionando la lógica principal, la interacción con NLU, el scraping web, el monitoreo del sistema y la síntesis de voz.
*   **Servidores (WS + HTTP):** Configura un servidor WebSocket para la comunicación en tiempo real con el HUD y un servidor HTTP para servir la interfaz web `index.html`.
