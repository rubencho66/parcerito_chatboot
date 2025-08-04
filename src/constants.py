import os

NOT_AUTHENTICATED_MESSAGE = "No estás autenticado. Inicia sesión para chatear."
MODEL_NOT_DEFINED = "Parcerito-bot no se está sintiendo muy bien. Por favor, comunicate con el administrador."
MODEL_FAILURE_MESSAGE = "Uy parcero... algo falló al generar tu respuesta. Intentálo de nuevo en un momentico."
RATE_LIMIT_MESSAGE = "¡Uy parcero! Parece que estás enviando mensajes muy rápido. Esperá un momentico y volvé a intentarlo."
DEFAULT_SYSTEM_PROMPT = "Eres Parcerito, el asistente virtual de ParceroGo. Responde solo preguntas relacionadas con ParceroGo usando el contexto proporcionado."

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(PROJECT_ROOT, "data")
KNOWLEDGE_BASE_PATH = os.path.join(DATA_PATH, "knowledge_base")
PROMPT_PATH = os.path.join(DATA_PATH, "prompt", "prompt.md")
