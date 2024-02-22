from fastapi import APIRouter, HTTPException

from ..crud import create_menuitem, delete_menuitem, get_menuitem_by_id, get_menuitems, update_menuitem
from ..schemas import MenuItemCreateRequest, MenuItemResponse, MenuItemUpdateRequest, PyObjectId


router = APIRouter(
    prefix="/menuitems",
    tags=["MenuItems"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=MenuItemResponse)
async def post_menuitem_handler(request: MenuItemCreateRequest):
    new_id = await create_menuitem(request)
    return await get_menuitem_by_id(new_id)

@router.get("/", response_model=list[MenuItemResponse])
async def get_menuitems_handler():
    return await get_menuitems()

@router.get("/{menuitem_id}", response_model=MenuItemResponse)
async def get_menuitem_handler(menuitem_id: PyObjectId):
    menuitem = await get_menuitem_by_id(menuitem_id)
    if menuitem:
        return menuitem
    raise HTTPException(status_code=404, detail="MenuItem not found")

@router.patch("/{menuitem_id}", response_model=MenuItemResponse)
async def patch_menuitem_handler(menuitem_id: PyObjectId, request: MenuItemUpdateRequest):
    updated_menuitem = await update_menuitem(menuitem_id, request)
    if updated_menuitem:
        return await get_menuitem_by_id(menuitem_id)
    raise HTTPException(status_code=404, detail="MenuItem not found")

@router.delete("/{menuitem_id}", response_model=MenuItemResponse)
async def delete_menuitem_handler(menuitem_id: PyObjectId):
    deleted_menuitem = await delete_menuitem(menuitem_id)
    if deleted_menuitem:
        return deleted_menuitem
    raise HTTPException(status_code=404, detail="MenuItem not found")
