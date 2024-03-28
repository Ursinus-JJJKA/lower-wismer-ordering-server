from fastapi import APIRouter

from ..crud import get_menunames, get_menuitems_by_menu
from ..schemas import MenuItemResponse


router = APIRouter(
    prefix="/menus",
    tags=["Menus"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=list[str])
async def get_menunames_handler():
    return await get_menunames()

@router.get("/{menu_name}", response_model=list[MenuItemResponse])
async def get_menuitems_by_name_handler(menu_name: str):
    menuitems = await get_menuitems_by_menu(menu_name)
    return menuitems
