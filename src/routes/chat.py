from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas import ChatRequest, ChatResponse, SecurityContext
from src.constants import MODEL_NOT_DEFINED
from src.security.auth import get_security_context
from src.dependencies import get_db
from src.chat_model import ChatModel
import logging

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)
model = ChatModel()

@router.post("", response_model=ChatResponse, response_model_exclude_none=True)
def chat(
    request: ChatRequest,
    security_context: SecurityContext = Depends(get_security_context),
    db: Session = Depends(get_db),
):
    logger.info("Chat request received: %s", request.message)
    chat_response = model.ask_to_model(request.message)
    if not chat_response:
        logger.error("Chat model not defined or failed to respond")
        raise HTTPException(status_code=500, detail=MODEL_NOT_DEFINED)
    logger.info("Chat response: %s", chat_response.content)
    return ChatResponse(
        reply=chat_response.content,
        statusCode=200,
        conversation_id=request.conversation_id,
    )
