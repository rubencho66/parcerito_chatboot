from dotenv import load_dotenv
import os

load_dotenv()

CONNECTION = os.getenv("CONNECTION")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM= os.getenv("ALGORITHM")
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
