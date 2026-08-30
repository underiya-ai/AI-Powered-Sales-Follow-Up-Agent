from pydantic import BaseModel,EmailStr
from typing import Literal


class EmailApprovalRequest(BaseModel):
    action: Literal["approve", "reject"]


class EmailEditRequest(BaseModel):
    subject: str
    body: str 




class CustomerEmailRequest(BaseModel):
    customer_email: EmailStr