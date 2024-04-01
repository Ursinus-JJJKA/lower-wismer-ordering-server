from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from ..crud import get_user_by_username, update_user
from ..dependencies import get_current_user
from ..exceptions import FailedLoginException, ScopeSelectionException, UnauthorizedUserException, UserNotFoundException
from ..schemas import Token, TokenData, UserResponse, UserUpdateRequest
from ..security import authenticate_jwt, create_access_token, verify_password


router = APIRouter(
    tags=["Account"]
)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Attempt to authenticate using the given username and password"""
    user = await get_user_by_username(form_data.username, include_hashed_password=True)
    if not user:
        raise FailedLoginException()
    if not verify_password(form_data.password, user["hashed_password"]):
        raise FailedLoginException()
    if len(form_data.scopes)!=1:
        raise ScopeSelectionException()
    desired_role = form_data.scopes[0]
    if desired_role not in user["roles"]:
        raise UnauthorizedUserException()
    # The create_access_token func will generate the correct exp time
    access_token = create_access_token({"sub":str(user["_id"]), "username":user["username"], "role":desired_role})
    return Token(access_token=access_token, token_type="bearer")

@router.get("/profile", response_model=UserResponse)
async def get_profile(user: dict = Depends(get_current_user)):
    """Get the profile of the current user"""
    return user

@router.post("/changepassword", status_code=204)
async def change_password(newpassword: str, verified_token_data: TokenData = Depends(authenticate_jwt)):
    """Change the password of the current user"""
    updated_user = await update_user(verified_token_data.sub, UserUpdateRequest(password=newpassword))
    if updated_user:
        return None
    raise UserNotFoundException()
