from fastapi import APIRouter, HTTPException

from ..database import get_collection
from ..schemas import UserCreateRequest, UserResponse, UserUpdateRequest, PyObjectId


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=UserResponse)
async def post_user_handler(user: UserCreateRequest):
    result = await get_collection("users").insert_one(user.model_dump())
    return UserResponse(**user.model_dump(),_id=result.inserted_id)

@router.get("/", response_model=list[UserResponse])
async def get_users_handler():
    return await get_collection("users").find({}).to_list(length=None)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_handler(user_id: PyObjectId):
    user = await get_collection("users").find_one({"_id": user_id})
    if user:
        return user
    raise HTTPException(status_code=404, detail=f"User not found")

async def general_update_user_handler(user_id: PyObjectId, user: UserCreateRequest, exclude_unset):
    updated_user = await get_collection("users").find_one_and_update(
        {"_id": user_id}, {"$set": user.model_dump(exclude_unset=exclude_unset)}
    )
    if updated_user:
        return await get_user_handler(user_id)
    raise HTTPException(status_code=404, detail="User not found")

@router.put("/{user_id}", response_model=UserResponse)
async def put_user_handler(user_id: PyObjectId, user: UserCreateRequest):
    return await general_update_user_handler(user_id, user, exclude_unset=False)

@router.patch("/{user_id}", response_model=UserResponse)
async def patch_user_handler(user_id: PyObjectId, user: UserUpdateRequest):
    return await general_update_user_handler(user_id, user, exclude_unset=True)

@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user_handler(user_id: PyObjectId):
    deleted_user = await get_collection("users").find_one_and_delete({"_id": user_id})
    if deleted_user:
        return deleted_user
    raise HTTPException(status_code=404, detail="User not found")