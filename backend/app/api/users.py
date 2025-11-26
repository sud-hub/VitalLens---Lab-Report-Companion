from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.db.models import User
from app.schemas.users import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile information.
    
    Requirements:
    - 2.4: Authenticate user with valid JWT token
    - 2.5: Reject request with invalid/expired token (handled by dependency)
    """
    return current_user
