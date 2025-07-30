from fastapi import APIRouter, HTTPException
from .schemas import RewriteRequest, RewriteResponse
from .services import RewriteService

router = APIRouter(prefix="/api/v1", tags=["rewrite"])
rewrite_service = RewriteService()

@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite_text(request: RewriteRequest):
    try:
        result = await rewrite_service.analyze_and_rewrite(request)
        return result
    except Exception as e:
        raise HTTPException(500, f"리라이팅 실패: {str(e)}")