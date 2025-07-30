from pydantic import BaseModel
from enum import Enum
from typing import List


class ContextType(str, Enum):
    BUSINESS_EMAIL = "business-email"
    ACADEMIC = "academic"
    CASUAL = "casual"


class RewriteRequest(BaseModel):
    text: str
    context: ContextType


class RewriteVersion(BaseModel):
    name: str
    icon: str
    text: str
    explanation: str


class RewriteResponse(BaseModel):
    original_text: str
    context: str