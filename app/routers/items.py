from fastapi import APIRouter, HTTPException

from ..database import get_collection
from ..schemas import ItemCreateRequest, ItemResponse, ItemUpdateRequest, PyObjectId


router = APIRouter(
    prefix="/items",
    tags=["Items"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=ItemResponse)
async def post_item_handler(item: ItemCreateRequest):
    result = await get_collection("items").insert_one(item.model_dump())
    return ItemResponse(**item.model_dump(),_id=result.inserted_id)

@router.get("/", response_model=list[ItemResponse])
async def get_items_handler():
    return await get_collection("items").find({}).to_list(length=None)

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item_handler(item_id: PyObjectId):
    item = await get_collection("items").find_one({"_id": item_id})
    if item:
        return item
    raise HTTPException(status_code=404, detail=f"Item not found")

async def general_update_item_handler(item_id: PyObjectId, item: ItemCreateRequest, exclude_unset):
    updated_item = await get_collection("items").find_one_and_update(
        {"_id": item_id}, {"$set": item.model_dump(exclude_unset=exclude_unset)}
    )
    if updated_item:
        return await get_item_handler(item_id)
    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/{item_id}", response_model=ItemResponse)
async def put_item_handler(item_id: PyObjectId, item: ItemCreateRequest):
    return await general_update_item_handler(item_id, item, exclude_unset=False)

@router.patch("/{item_id}", response_model=ItemResponse)
async def patch_item_handler(item_id: PyObjectId, item: ItemUpdateRequest):
    return await general_update_item_handler(item_id, item, exclude_unset=True)

@router.delete("/{item_id}", response_model=ItemResponse)
async def delete_item_handler(item_id: PyObjectId):
    deleted_item = await get_collection("items").find_one_and_delete({"_id": item_id})
    if deleted_item:
        return deleted_item
    raise HTTPException(status_code=404, detail="Item not found")