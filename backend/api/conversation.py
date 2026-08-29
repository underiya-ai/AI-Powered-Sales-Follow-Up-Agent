from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from langgraph.types import Command
from backend.schema.conversation_schema import (EmailApprovalRequest,EmailEditRequest)

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


    # 1. Speech-to-Text
    

    transcript = await transcribe_audio(file)

    if not transcript:
        raise HTTPException(
            status_code=400,
            detail="Could not generate transcript"
        )

    
    # 2. Save conversation in database
    

    conversation = Conversation(
        conversation_type="call",
        filename=file.filename,
        transcript=transcript
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)


    # 3. Create LangGraph State
    

    initial_state = {
        "conversation_id": conversation.id,
        "conversation_type": "call",
        "filename": conversation.filename,
        "transcript": conversation.transcript
    }

    config = {
    "configurable": {
        "thread_id": str(conversation.id)
    }
}

    # 4. Run Sales AI Pipeline


    try:
        result = sales_graph.invoke(initial_state,config=config)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI pipeline failed: {str(exc)}"
        )

    
    # 5. Return transcript + AI analysis
    

    return {
    "success": True,
    "conversation_id": conversation.id,
    "conversation_type": "call",
    "filename": conversation.filename,

    "transcript": conversation.transcript,

    "conversation_analysis": result.get(
        "conversation_analysis"
    ),

    "lead_score": result.get(
        "lead_score"
    ),

    "lead_priority": result.get(
        "lead_priority"
    ),

    "lead_scoring_reason": result.get(
        "lead_scoring_reason"
    ),

    "next_best_action": result.get(
        "next_best_action"
    ),

    "follow_up": result.get(
        "follow_up"
    ),

    "email": result.get(
    "email"
    ),

    "created_at": conversation.created_at
}

@router.post("/{conversation_id}/approve")
async def approve_email(
    conversation_id: int,
    request: EmailApprovalRequest,
    db: Session = Depends(get_db)
):

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    if request.action != "approve":
        raise HTTPException(
            status_code=400,
            detail="Action must be approve"
        )

    config = {
        "configurable": {
            "thread_id": str(conversation_id)
        }
    }

    result = sales_graph.invoke(
        Command(
            resume={
                "action": "approve"
            }
        ),
        config=config
    )

    conversation.approval_status = "approved"

    db.commit()

    return {
        "success": True,
        "conversation_id": conversation_id,
        "approval_status": "approved",
        "message": "Email approved successfully.",
        "result": result
    } 

@router.post("/{conversation_id}/edit")
async def edit_email(
    conversation_id: int,
    request: EmailEditRequest,
    db: Session = Depends(get_db)
):

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    config = {
        "configurable": {
            "thread_id": str(conversation_id)
        }
    }

    edited_email = {
        "subject": request.subject,
        "body": request.body
    }

    result = sales_graph.invoke(
        Command(
            resume={
                "action": "edit",
                "email": edited_email
            }
        ),
        config=config
    )

    conversation.email_subject = request.subject
    conversation.email_body = request.body
    conversation.approval_status = "edited"

    db.commit()

    return {
        "success": True,
        "conversation_id": conversation_id,
        "approval_status": "edited",
        "email": edited_email,
        "message": "Email edited successfully.",
        "result": result
    }


@router.post("/{conversation_id}/reject")
async def reject_email(
    conversation_id: int,
    db: Session = Depends(get_db)
):

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    config = {
        "configurable": {
            "thread_id": str(conversation_id)
        }
    }

    result = sales_graph.invoke(
        Command(
            resume={
                "action": "reject"
            }
        ),
        config=config
    )

    conversation.approval_status = "rejected"

    db.commit()

    return {
        "success": True,
        "conversation_id": conversation_id,
        "approval_status": "rejected",
        "message": "Email rejected. It will not be sent.",
        "result": result
    }