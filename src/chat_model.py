import os

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langgraph.graph import MessagesState
from langchain.chat_models import init_chat_model


class ChatModel:
    retriever_tool = None

    def _get_knowledge_base_files(self, knowledge_base_path: str) -> list[str]:
        """
        Retrieves a list of file paths for all Markdown (.md) files in the specified knowledge base directory.

        Args:
            knowledge_base_path (str): The path to the directory containing the knowledge base files.

        Returns:
            list[str]: A list of file paths for all Markdown files in the specified directory.
        """
        markdown_paths = []
        for filename in os.listdir(knowledge_base_path):
            if filename.endswith(".md"):
                markdown_paths.append(os.path.join(knowledge_base_path, filename))
        return markdown_paths

    def _get_documents(self, markdown_path: list[str]) -> list[TextLoader]:
        """
        Loads and flattens documents from a list of markdown file paths.

        Args:
            markdown_path (list[str]): A list of file paths to markdown files.

        Returns:
            list[TextLoader]: A flattened list of TextLoader objects containing the loaded content
            from the provided markdown files.
        """
        documents = [
            TextLoader(markdown_file, encoding="utf-8").load()
            for markdown_file in markdown_path
        ]
        return [item for sublist in documents for item in sublist]

    def _get_splitted_docs(self, document_list):
        """
        Splits a list of documents into smaller chunks using a RecursiveCharacterTextSplitter.

        Args:
            document_list (list): A list of documents to be split. Each document should be a string or an object compatible with the text splitter.

        Returns:
            list: A list of smaller document chunks obtained by splitting the input documents.
        """
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=100, chunk_overlap=50
        )
        docs_splits = text_splitter.split_documents(document_list)
        return docs_splits

    def _create_memory_db(self, docs_splits):
        """
        Creates an in-memory vector store from a list of document splits.

        This function uses the InMemoryVectorStore to store the provided document
        splits and applies OpenAIEmbeddings to generate embeddings for the documents.

        Args:
            docs_splits (list): A list of document splits to be stored in the vector store.

        Returns:
            InMemoryVectorStore: An in-memory vector store containing the embedded documents.
        """
        vectorstore = InMemoryVectorStore.from_documents(
            documents=docs_splits, embedding=OpenAIEmbeddings()
        )
        return vectorstore

    def _create_retriever(
        self, vectorstore: InMemoryVectorStore, name: str, description: str
    ):
        """
        Creates a retriever tool from the given vector store.

        Args:
            vectorstore (InMemoryVectorStore): The in-memory vector store to be used for retrieval.
            name (str): The name of the retriever tool.
            description (str): A brief description of the retriever tool.

        Returns:
            Tool: A retriever tool created from the provided vector store.
        """
        retriever = vectorstore.as_retriever()
        return create_retriever_tool(retriever, name, description)

    def __init__(self):
        "Instanciate the chat model with the appropriate parameters"
        kb_path = "knowledge_base"
        model_temperature = 0.3
        self.response_model = init_chat_model(
            "openai:gpt-4.1", temperature=model_temperature
        )

        # 1. cargar el contenido
        markdown_files = self._get_knowledge_base_files(kb_path)
        document_list = self._get_documents(markdown_files)

        # 2. separar el texto y codificar con el embedding (tiktoken_encoder)
        docs_splits = self._get_splitted_docs(document_list)
        vectorstore = self._create_memory_db(docs_splits)
        self.retriever_tool = self._create_retriever(
            vectorstore,
            "retrieve_ParceroGo",
            "Buscador de información parceroGo",
        )

    def _generate_response(self, message: str):
        # utilizar la base de datos
        input_message = {"messages": [{"role": "user", "content": message}]}
        docs = self.retriever_tool.invoke(
            {"query": input_message["messages"][-1]["content"]}
        )
        full_prompt = f"Contexto:\n{docs}\n\nPregunta del usuario: {input_message['messages'][-1]['content']}"
        return self.response_model.invoke(full_prompt)

    def ask_to_model(self, message: str, conversation_id: str):
        "Ask the model a question and return the response"
        if not self.retriever_tool and not self.response_model:
            return None
        response = self._generate_response(message)
        return response
