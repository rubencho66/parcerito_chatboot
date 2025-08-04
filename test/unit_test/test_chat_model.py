import pytest

from openai import RateLimitError
from unittest.mock import MagicMock

from src.chat_model import ChatModel
from src.constants import MODEL_FAILURE_MESSAGE, MODEL_NOT_DEFINED, RATE_LIMIT_MESSAGE
from src.schemas import LLMResponse
from starlette.exceptions import HTTPException

@pytest.fixture
def chat_model():
    mock_retriever = MagicMock()
    mock_response_model = MagicMock()
    return ChatModel(
        response_model=mock_response_model,
        retriever_tool=mock_retriever,
        prompt_path="mock_prompt.md",
        knowledge_base_path="mock_kb/"
    )

def test_generate_response_calls_local_model(chat_model):
    chat_model.use_local_model = True
    chat_model.retriever_tool.invoke.return_value = [MagicMock(page_content="context")]
    chat_model._call_local_model = MagicMock(return_value="response")
    result = chat_model._generate_response("hello")
    assert result == "response"
    chat_model._call_local_model.assert_called_once()

def test_generate_response_calls_openai(chat_model):
    chat_model.use_local_model = False
    chat_model.retriever_tool.invoke.return_value = [MagicMock(page_content="context")]
    chat_model.response_model.invoke.return_value = "response"
    result = chat_model._generate_response("hello")
    assert result == "response"
    chat_model.response_model.invoke.assert_called_once()

def test_ask_to_model_success(chat_model):
    chat_model._generate_response = MagicMock(return_value="response")
    result = chat_model.ask_to_model("hello")
    assert isinstance(result, LLMResponse)
    assert result.content == "response"

def test_ask_to_model_rate_limit(chat_model):
    chat_model._generate_response = MagicMock(side_effect=RateLimitError("fail", response=MagicMock(), body=MagicMock()))
    with pytest.raises(HTTPException) as exc:
        chat_model.ask_to_model("hello")
    assert exc.value.status_code == 429
    assert exc.value.detail == RATE_LIMIT_MESSAGE

def test_ask_to_model_failure(chat_model):
    chat_model._generate_response = MagicMock(side_effect=Exception("fail"))
    with pytest.raises(HTTPException) as exc:
        chat_model.ask_to_model("hello")
    assert exc.value.status_code == 500
    assert exc.value.detail == MODEL_FAILURE_MESSAGE

def test_ask_to_model_no_response(chat_model):
    chat_model._generate_response = MagicMock(return_value=None)
    with pytest.raises(HTTPException) as exc:
        chat_model.ask_to_model("hello")
    assert exc.value.status_code == 500
    assert exc.value.detail == MODEL_NOT_DEFINED
