from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from langgraph.types import Command

from backend.schema.conversation_schema import (
    EmailApprovalRequest,
    EmailEditRequest,
    CustomerEmailRequest,
    EmailConversationRequest
)

from backend.service.transcription import transcribe_audio
from backend.service.database import SessionLocal, Conversation
from backend.pipeline.graph import sales_graph, email_graph


router = APIRouter(
    prefix="/api/v1/conversations",
    tags=["Conversations"]
)


# ==================================================
# DATABASE
# ==================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==================================================
# CALL CONVERSATION
# ==================================================

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

    # ----------------------------------------------
    # Speech to Text
    # ----------------------------------------------

    transcript = await transcribe_audio(file)

    if not transcript:
        raise HTTPException(
            status_code=400,
            detail="Could not generate transcript"
        )

    # ----------------------------------------------
    # Save conversation
    # ----------------------------------------------

    conversation = Conversation(
        conversation_type="call",
        filename=file.filename,
        transcript=transcript
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    # ----------------------------------------------
    # LangGraph state
    # ----------------------------------------------

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

    # ----------------------------------------------
    # Run Sales Graph
    # ----------------------------------------------

    try:

        result = sales_graph.invoke(
            initial_state,
            config=config
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"AI pipeline failed: {str(exc)}"
        )

    # ----------------------------------------------
    # Response
    # ----------------------------------------------

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

        "created_at": conversation.created_at
    }


# ==================================================
# EMAIL CONVERSATION
# ==================================================

@router.post("/email")
async def analyze_email(
    request: EmailConversationRequest,
    db: Session = Depends(get_db)
):

    if not request.email_body:
        raise HTTPException(
            status_code=400,
            detail="Email body is required"
        )

    transcript = f"""Subject: {request.email_subject}

{request.email_body}
"""

    # ----------------------------------------------
    # Save conversation
    # ----------------------------------------------

    conversation = Conversation(
        conversation_type="email",
        filename="email",
        transcript=transcript
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    # ----------------------------------------------
    # LangGraph state
    # ----------------------------------------------

    initial_state = {
        "conversation_id": conversation.id,
        "conversation_type": "email",
        "filename": "email",
        "transcript": transcript
    }

    config = {
        "configurable": {
            "thread_id": str(conversation.id)
        }
    }

    # ----------------------------------------------
    # Run Sales Graph
    # ----------------------------------------------

    try:

        result = sales_graph.invoke(
            initial_state,
            config=config
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"AI pipeline failed: {str(exc)}"
        )

    return {
        "success": True,
        "conversation_id": conversation.id,
        "conversation_type": "email",
        "transcript": transcript,

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
        )
    }


# ==================================================
# GENERATE FOLLOW-UP EMAIL
# ==================================================

@router.post("/{conversation_id}/generate-email")
async def generate_email(
    conversation_id: int,
    request: CustomerEmailRequest,
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

    if not request.customer_email:
        raise HTTPException(
            status_code=400,
            detail="Customer email is required"
        )

    config = {
        "configurable": {
            "thread_id": str(conversation_id)
        }
    }

    try:

        # Get state created by sales graph
        checkpoint = sales_graph.get_state(config)

        if not checkpoint or not checkpoint.values:
            raise HTTPException(
                status_code=400,
                detail="Conversation pipeline state not found"
            )

        state = dict(checkpoint.values)

        # Add customer email
        state["customer_email"] = str(
            request.customer_email
        )

        # Run email generation graph
        result = email_graph.invoke(
            state,
            config=config
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Email generation failed: {str(exc)}"
        )

    # ----------------------------------------------
    # Get generated email
    # ----------------------------------------------

    generated_email = result.get("email")

    if not generated_email:
        raise HTTPException(
            status_code=500,
            detail="Email generation returned no email"
        )

    # ----------------------------------------------
    # Save generated email
    # ----------------------------------------------

    conversation.email_subject = generated_email.get(
        "subject"
    )

    conversation.email_body = generated_email.get(
        "body"
    )

    conversation.approval_status = "pending"

    db.commit()
    db.refresh(conversation)

    return {
        "success": True,
        "conversation_id": conversation_id,
        "customer_email": request.customer_email,

        "email": generated_email,

        "lead_score": result.get(
            "lead_score"
        ),

        "lead_priority": result.get(
            "lead_priority"
        ),

        "next_best_action": result.get(
            "next_best_action"
        ),

        "follow_up": result.get(
            "follow_up"
        )
    }


# ==================================================
# EDIT EMAIL
# IMPORTANT:
# EDIT DOES NOT SEND EMAIL
# ==================================================

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

    # ----------------------------------------------
    # Validate edited email
    # ----------------------------------------------

    if not request.subject.strip():
        raise HTTPException(
            status_code=400,
            detail="Email subject is required"
        )

    if not request.body.strip():
        raise HTTPException(
            status_code=400,
            detail="Email body is required"
        )

    edited_email = {
        "subject": request.subject,
        "body": request.body
    }

    config = {
        "configurable": {
            "thread_id": str(conversation_id)
        }
    }

    try:

        # ------------------------------------------
        # Get current EMAIL GRAPH state
        # ------------------------------------------

        checkpoint = email_graph.get_state(config)

        if not checkpoint or not checkpoint.values:
            raise HTTPException(
                status_code=400,
                detail="Email graph state not found"
            )

        state = dict(checkpoint.values)

        # ------------------------------------------
        # Replace email with EDITED email
        # ------------------------------------------

        state["email"] = edited_email

        state["approval_status"] = "edited"
        state["human_approval"] = "edited"
        state["pipeline_status"] = "email_edited"

        # ------------------------------------------
        # IMPORTANT
        # Save edited email to graph checkpoint
        # ------------------------------------------

        email_graph.update_state(
            config,
            state
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Email edit failed: {str(exc)}"
        )

    # ----------------------------------------------
    # Save edited email to DATABASE
    # ----------------------------------------------

    conversation.email_subject = request.subject
    conversation.email_body = request.body
    conversation.approval_status = "edited"

    db.commit()
    db.refresh(conversation)

    return {
        "success": True,
        "conversation_id": conversation_id,

        "approval_status": "edited",

        "email": edited_email,

        "pipeline_status": "email_edited",

        "message": (
            "Email edited successfully. "
            "Click Approve & Send to send this email."
        )
    }


#approve end point

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

    try:

     
        # Get latest EMAIL GRAPH state
        

        checkpoint = email_graph.get_state(config)

        if not checkpoint or not checkpoint.values:
            raise HTTPException(
                status_code=400,
                detail="Email graph state not found"
            )

        state = dict(checkpoint.values)

       # Get latest email
        # This should be the EDITED email if user
        # edited it.
       

        email = state.get("email")

        # Fallback to database if needed
        if not email:

            if not conversation.email_subject or not conversation.email_body:
                raise HTTPException(
                    status_code=400,
                    detail="No email available to send"
                )

            email = {
                "subject": conversation.email_subject,
                "body": conversation.email_body
            }

        
        # Make latest email explicit
       

        state["email"] = {
            "subject": email["subject"],
            "body": email["body"]
        }

        state["approval_status"] = "approved"
        state["human_approval"] = "approved"
        state["pipeline_status"] = "email_approved"

        
        # Save latest state
       

        email_graph.update_state(
            config,
            state
        )

        
        # Resume email graph
        #
        # This is where send_email node should run.
      

        result = email_graph.invoke(
            Command(
                resume={
                    "action": "approve"
                }
            ),
            config=config
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Email approval failed: {str(exc)}"
        )

   
    # Save final email in database
   

    conversation.email_subject = email["subject"]
    conversation.email_body = email["body"]
    conversation.approval_status = "approved"

    db.commit()
    db.refresh(conversation)

    return {
        "success": True,
        "conversation_id": conversation_id,

        "approval_status": "approved",

        "email": email,

        "pipeline_status": result.get(
            "pipeline_status",
            "email_sent"
        ),

        "message": "Email sent successfully!"
    }


# REJECT EMAIL

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

    try:

        result = email_graph.invoke(
            Command(
                resume={
                    "action": "reject"
                }
            ),
            config=config
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Email rejection failed: {str(exc)}"
        )

    conversation.approval_status = "rejected"

    db.commit()
    db.refresh(conversation)

    return {
        "success": True,
        "conversation_id": conversation_id,
        "approval_status": "rejected",

        "message": (
            "Email rejected. "
            "It was not sent."
        ),

        "result": result
    }