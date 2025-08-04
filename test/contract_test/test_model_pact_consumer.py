from time import sleep
import pytest
from pact import Consumer, Provider, Like, Term
import requests

PACT_MOCK_HOST = 'localhost'
PACT_MOCK_PORT = 8090
PACT_URL = f'http://{PACT_MOCK_HOST}:{PACT_MOCK_PORT}/v1/chat/completions'

pact = Consumer('ParceroGoConsumer').has_pact_with(
    Provider('ChatModelProvider'),
    host_name=PACT_MOCK_HOST,
    port=PACT_MOCK_PORT,
)

@pytest.fixture(scope='module')
def pact_setup():
    pact.start_service()
    sleep(10)  # Wait for the service to start
    yield
    pact.stop_service()

@pytest.mark.contract
def test_chat_model_contract(pact_setup):
    expected_response = {
        "id": Like("chatcmpl-awqt3fcxps78anf05wet7t"),
        "object": Term(r"chat.completion", "chat.completion"),
        "created": Like(1754485000),
        "model": Like("google/gemma-3n-e4b"),
        "choices": Like([
            {
                "index": Like(0),
                "logprobs": None,
                "finish_reason": Term(r"stop", "stop"),
                "message": {
                    "role": Term(r"assistant", "assistant"),
                    "content": Like("¡Claro que sí! Para eso estoy, parcero. ¿En qué te puedo ayudar con ParceroGo?")
                }
            }
        ]),
        "usage": {
            "prompt_tokens": Like(2185),
            "completion_tokens": Like(24),
            "total_tokens": Like(2209)
        },
        "stats": Like({}),
        "system_fingerprint": Like("google/gemma-3n-e4b")
    }

    pact.given('A valid chat request')\
        .upon_receiving('a chat completion request')\
        .with_request(
            method='POST',
            path='/v1/chat/completions',
            headers={'Authorization': Like('Bearer sometoken'), 'Content-Type': 'application/json'},
            body={
                "message": "Hello",
                "conversation_id": "abc123"
            }
        )\
        .will_respond_with(
            status=200,
            headers={'Content-Type': 'application/json'},
            body=expected_response
        )

    with pact:
        response = requests.post(
            PACT_URL,
            json={"message": "Hello", "conversation_id": "abc123"},
            headers={"Authorization": "Bearer sometoken", "Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) >= set(expected_response.keys())
        assert data["object"] == "chat.completion"
        assert data["choices"][0]["message"]["role"] == "assistant"
        assert isinstance(data["choices"], list)
        assert "content" in data["choices"][0]["message"]
