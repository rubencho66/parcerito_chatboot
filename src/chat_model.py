from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langgraph.graph import MessagesState
from langchain.chat_models import init_chat_model

def instanciate_chat_model():
    model_temperature = 0 # todo: Colocar la temperatura adecuada según lo aprendido
    response_model = init_chat_model("openai:gpt-4.1", temperature=model_temperature)
    return response_model

def ask_to_model(model, message: str, conversation_id: str):
    if not model:
        return None
    response = model.invoke(message).content
    return response
    