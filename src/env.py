"""Environment variable loading and configuration for the application.
This module loads environment variables from a .env file and provides configuration constants."""
import os

from dotenv import load_dotenv

load_dotenv()

CONNECTION = os.getenv("CONNECTION")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM= os.getenv("ALGORITHM")
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Configuración para modelo local
USE_LOCAL_MODEL = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "meta-llama-3.1-8b-instruct")
LOCAL_LLM_BASE_URL = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:1234/v1")
LOCAL_LLM_API_KEY = os.getenv("LOCAL_LLM_API_KEY", "lm-studio")
