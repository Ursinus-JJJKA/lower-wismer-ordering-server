from fastapi import APIRouter, Depends

from ..crud import create_user, delete_user, get_user_by_id, get_users, update_user
from ..dependencies import assert_admin_access
from ..exceptions import UnauthorizedUserException, UserNotFoundException
from ..schemas import PyObjectId, Role, TokenData, UserCreateRequest, UserResponse, UserUpdateRequest


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=UserResponse, status_code=201)
async def post_user_handler(request: UserCreateRequest, verified_token_data: TokenData = Depends(assert_admin_access)):
    if Role.superadmin in request.roles and verified_token_data.role != Role.superadmin:
        raise UnauthorizedUserException()
    new_id = await create_user(request)
    return await get_user_by_id(new_id)

@router.get("/", response_model=list[UserResponse])
async def get_users_handler(verified_token_data: TokenData = Depends(assert_admin_access)):
    return await get_users()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_handler(user_id: PyObjectId, verified_token_data: TokenData = Depends(assert_admin_access)):
    user = await get_user_by_id(user_id)
    if user:
        return user
    raise UserNotFoundException()

@router.patch("/{user_id}", response_model=UserResponse)
async def patch_user_handler(user_id: PyObjectId, request: UserUpdateRequest, verified_token_data: TokenData = Depends(assert_admin_access)):
    #TODO add safeguards to prevent admins from removing each other, there should always be an admin
    if request.roles and Role.superadmin in request.roles and verified_token_data.role != Role.superadmin:
        raise UnauthorizedUserException()
    updated_user = await update_user(user_id, request)
    if updated_user:
        return updated_user
    raise UserNotFoundException()

@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user_handler(user_id: PyObjectId, verified_token_data: TokenData = Depends(assert_admin_access)):
    #TODO add safeguards to prevent admins from removing each other, there should always be an admin
    deleted_user = await delete_user(user_id)
    if deleted_user:
        return deleted_user
    raise UserNotFoundException()
