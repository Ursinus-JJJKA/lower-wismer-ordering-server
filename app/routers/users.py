from fastapi import APIRouter, HTTPException

from ..crud import create_user, delete_user, get_user_by_id, get_users, update_user
from ..schemas import PyObjectId, UserCreateRequest, UserResponse, UserUpdateRequest


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=UserResponse)
async def post_user_handler(request: UserCreateRequest):
    new_id = await create_user(request)
    return await get_user_by_id(new_id)

@router.get("/", response_model=list[UserResponse])
async def get_users_handler():
    return await get_users()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_handler(user_id: PyObjectId):
    user = await get_user_by_id(user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@router.patch("/{user_id}", response_model=UserResponse)
async def patch_user_handler(user_id: PyObjectId, request: UserUpdateRequest):
    updated_user = await update_user(user_id, request)
    if updated_user:
        return await get_user_by_id(user_id)
    raise HTTPException(status_code=404, detail="User not found")

@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user_handler(user_id: PyObjectId):
    deleted_user = await delete_user(user_id)
    if deleted_user:
        return deleted_user
    raise HTTPException(status_code=404, detail="User not found")
