from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.service.transcription import transcribe_audio


router = APIRouter(
    prefix="/api/v1/conversations",
    tags=["Conversations"]
)


@router.post("/call")
async def transcribe_call(
    file: UploadFile = File(...)
):
    """
    Upload a call recording and convert it into a transcript.
    """

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

    transcript = await transcribe_audio(file)

    return {
        "success": True,
        "conversation_type": "call",
        "filename": file.filename,
        "transcript": transcript
    }