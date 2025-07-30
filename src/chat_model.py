from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langgraph.graph import MessagesState
from langchain.chat_models import init_chat_model
from starlette.exceptions import HTTPException
from openai import RateLimitError, Timeout, APIError
from .constants import MODEL_FAILURE_MESSAGE, RATE_LIMIT_MESSAGE, MODEL_NOT_DEFINED

def instanciate_chat_model():
    model_temperature = 0 # todo: Colocar la temperatura adecuada según lo aprendido
    response_model = init_chat_model("openai:gpt-4.1", temperature=model_temperature)
    return response_model

def ask_to_model(model, message: str, conversation_id: str):
    if not model:
        raise HTTPException(status_code=500, detail=MODEL_NOT_DEFINED)
    
    try:
        response = model.invoke(message).content
    except RateLimitError:
        raise HTTPException(status_code=429, detail=RATE_LIMIT_MESSAGE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=MODEL_FAILURE_MESSAGE)
    
    if not response:
        raise HTTPException(status_code=500, detail=MODEL_NOT_DEFINED)
    
    return response
    