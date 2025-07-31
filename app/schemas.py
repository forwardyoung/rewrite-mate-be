from pydantic import BaseModel
from enum import Enum


class ContextType(str, Enum):
    BUSINESS_EMAIL = "business-email"
    ACADEMIC = "academic"
    CASUAL = "casual"


class RewriteRequest(BaseModel):
    text: str
    context: ContextType
    tone: str  # 선택된 톤


class RewriteResponse(BaseModel):
    original_text: str
    context: str
    rewritten_text: str
    explanation: str
    tone_name: str
    tone_icon: str