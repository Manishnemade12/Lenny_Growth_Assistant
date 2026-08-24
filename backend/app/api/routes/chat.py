"""FastAPI SSE and JSON chat API routes."""

import json
import logging
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.orchestrator import AgentOrchestrator
from app.db.database import get_db
from app.schemas.chat import ChatRequest

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Chat endpoint supporting SSE streaming responses."""
    orchestrator = AgentOrchestrator()

    async def event_stream():
        try:
            yield f"event: message_start\ndata: {json.dumps({'status': 'started'})}\n\n"
            async for chunk in orchestrator.process_message_stream(
                session_id=request.session_id,
                message=request.message,
                db=db,
            ):
                if chunk["type"] == "content_delta":
                    yield f"event: content_delta\ndata: {json.dumps(chunk)}\n\n"
                elif chunk["type"] == "source_citations":
                    yield f"event: source_citations\ndata: {json.dumps(chunk)}\n\n"
            yield f"event: message_end\ndata: {json.dumps({'status': 'complete'})}\n\n"
        except Exception as exc:
            logger.error("SSE stream error", extra={"error": str(exc)})
            yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
