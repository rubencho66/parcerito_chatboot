import pytest
from fastapi import FastAPI
from threading import Thread
from pact import Verifier
import time
import os
import uvicorn

from src.constants import PROJECT_ROOT

PACT_FILE = os.path.join(PROJECT_ROOT, )
PROVIDER_URL = 'http://localhost:5002'

@pytest.fixture(scope='module')
def fastapi_server():
    app = FastAPI()

    @app.post('/chat')
    def chat(request: dict):
        # Mock del modelo: responde siempre con el mensaje esperado
        return {
            "reply": "Parce, creo que su dinero está en el lugar equivocado, eso no es conmigo.",
            "statusCode": 200,
            "conversation_id": request.get("conversation_id", "abcd")
        }

    server = Thread(target=uvicorn.run, args=(app,), kwargs={"host": "0.0.0.0", "port": 5002, "log_level": "info"})
    server.daemon = True
    server.start()
    time.sleep(10)
    yield

@pytest.mark.contract
def test_provider_contract(fastapi_server):
    verifier = Verifier(provider='ChatModelProvider', provider_base_url=PROVIDER_URL)
    output, _ = verifier.verify_pacts('./test/contract_test/parcerogoconsumer-chatmodelprovider.json', verbose=True)
    assert output == 0
