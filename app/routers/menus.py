from fastapi import APIRouter, HTTPException

from ..database import get_collection
from ..schemas import MenuCreateRequest, MenuResponse, MenuUpdateRequest, PyObjectId


router = APIRouter(
    prefix="/menus",
    tags=["Menus"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=MenuResponse)
async def post_menu_handler(menu: MenuCreateRequest):
    result = await get_collection("menus").insert_one(menu.model_dump())
    return MenuResponse(**menu.model_dump(),_id=result.inserted_id)

@router.get("/", response_model=list[MenuResponse])
async def get_menus_handler():
    return await get_collection("menus").find({}).to_list(length=None)

@router.get("/{menu_id}", response_model=MenuResponse)
async def get_menu_handler(menu_id: PyObjectId):
    menu = await get_collection("menus").find_one({"_id": menu_id})
    if menu:
        return menu
    raise HTTPException(status_code=404, detail=f"Menu not found")

async def general_update_menu_handler(menu_id: PyObjectId, menu: MenuCreateRequest, exclude_unset):
    updated_menu = await get_collection("menus").find_one_and_update(
        {"_id": menu_id}, {"$set": menu.model_dump(exclude_unset=exclude_unset)}
    )
    if updated_menu:
        return await get_menu_handler(menu_id)
    raise HTTPException(status_code=404, detail="Menu not found")

@router.put("/{menu_id}", response_model=MenuResponse)
async def put_menu_handler(menu_id: PyObjectId, menu: MenuCreateRequest):
    return await general_update_menu_handler(menu_id, menu, exclude_unset=False)

@router.patch("/{menu_id}", response_model=MenuResponse)
async def patch_menu_handler(menu_id: PyObjectId, menu: MenuUpdateRequest):
    return await general_update_menu_handler(menu_id, menu, exclude_unset=True)

@router.delete("/{menu_id}", response_model=MenuResponse)
async def delete_menu_handler(menu_id: PyObjectId):
    deleted_menu = await get_collection("menus").find_one_and_delete({"_id": menu_id})
    if deleted_menu:
        return deleted_menu
    raise HTTPException(status_code=404, detail="Menu not found")