from pydantic import BaseModel
from typing import Literal


class EmailApprovalRequest(BaseModel):
    action: Literal["approve", "reject"]


class EmailEditRequest(BaseModel):
    subject: str
    body: str 