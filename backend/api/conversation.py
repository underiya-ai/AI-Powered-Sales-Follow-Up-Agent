from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.service.transcription import transcribe_audio
from backend.service.database import SessionLocal, Conversation
from backend.pipeline.graph import sales_graph


router = APIRouter(
    prefix="/api/v1/conversations",
    tags=["Conversations"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/call")
async def transcribe_call(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )

    allowed_extensions = {
        ".mp3",
        ".wav",
        ".m4a",
        ".mp4",
        ".webm",
        ".ogg"
    }

    file_extension = "." + file.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported audio format"
        )

    # --------------------------------------------------
    # 1. Speech-to-Text
    # --------------------------------------------------

    transcript = await transcribe_audio(file)

    if not transcript:
        raise HTTPException(
            status_code=400,
            detail="Could not generate transcript"
        )

    # --------------------------------------------------
    # 2. Save conversation in database
    # --------------------------------------------------

    conversation = Conversation(
        conversation_type="call",
        filename=file.filename,
        transcript=transcript
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    # --------------------------------------------------
    # 3. Create LangGraph State
    # --------------------------------------------------

    initial_state = {
        "conversation_id": conversation.id,
        "conversation_type": "call",
        "filename": conversation.filename,
        "transcript": conversation.transcript
    }

    # --------------------------------------------------
    # 4. Run Sales AI Pipeline
    # --------------------------------------------------

    try:
        result = sales_graph.invoke(initial_state)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI pipeline failed: {str(exc)}"
        )

    # --------------------------------------------------
    # 5. Return transcript + AI analysis
    # --------------------------------------------------

    return {
        "success": True,
        "conversation_id": conversation.id,
        "conversation_type": "call",
        "filename": conversation.filename,

        "transcript": conversation.transcript,

        "conversation_analysis": result.get(
            "conversation_analysis"
        ),

        "created_at": conversation.created_at
    }