from fastapi import APIRouter, Depends

from ..crud import get_active_orders_by_kitchen, get_kitchennames
from ..dependencies import assert_kitchen_access
from ..schemas import OrderResponse, TokenData


router = APIRouter(
    prefix="/kitchens",
    tags=["Kitchens"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=list[str])
async def get_kitchennames_handler():
    return await get_kitchennames()

@router.get("/{kitchen_name}", response_model=list[OrderResponse])
async def get_orders_by_kitchen_handler(kitchen_name: str, verified_token_data: TokenData = Depends(assert_kitchen_access)):
    orders = await get_active_orders_by_kitchen(kitchen_name)
    return orders
