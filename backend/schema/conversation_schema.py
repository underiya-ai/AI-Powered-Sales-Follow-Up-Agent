from pydantic import BaseModel, EmailStr


class EmailConversationRequest(BaseModel):
    email_subject: str
    email_body: str


class CustomerEmailRequest(BaseModel):
    customer_email: EmailStr


class EmailApprovalRequest(BaseModel):
    action: str


class EmailEditRequest(BaseModel):
    subject: str
    body: str