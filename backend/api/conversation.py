from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends

from backend.service.transcription import transcribe_audio
from backend.service.database import SessionLocal, Conversation


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

    # Step 1: Convert audio to text
    transcript = await transcribe_audio(file)

    if not transcript:
        raise HTTPException(
            status_code=400,
            detail="Could not generate transcript"
        )

    # Step 2: Save conversation in database
    conversation = Conversation(
        conversation_type="call",
        filename=file.filename,
        transcript=transcript
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {
        "success": True,
        "conversation_id": conversation.id,
        "conversation_type": "call",
        "filename": conversation.filename,
        "transcript": conversation.transcript,
        "created_at": conversation.created_at
    }