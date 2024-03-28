from fastapi import APIRouter

from ..crud import create_user, get_user_by_id, update_user
from ..exceptions import CredentialsException, UserNotFoundException
from ..schemas import PyDecimal128, PyObjectId, UserCreateRequest, UserResponse, UserUpdateRequest
from ..security import authenticate_jwt


router = APIRouter(
    prefix="/demo",
    tags=["Demo"]
)

@router.post("/register", response_model=UserResponse)
async def register_user_handler(request: UserCreateRequest):
    new_id = await create_user(request)
    return await get_user_by_id(new_id)

@router.post("/setbalance", response_model=UserResponse)
async def set_balance_handler(user_id: PyObjectId, new_balance: PyDecimal128):
    updated_user = await update_user(user_id, UserUpdateRequest(balance=new_balance))
    if updated_user:
        return updated_user
    raise UserNotFoundException()

@router.post("/verifyjwt")
async def verify_jwt_handler(jwt: str):
    try:
        return authenticate_jwt(jwt)
    except CredentialsException:
        return False
