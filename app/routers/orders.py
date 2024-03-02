from fastapi import APIRouter

from ..crud import get_orders, get_order_by_id, place_order, update_order
from ..exceptions import OrderNotFoundException
from ..schemas import OrderCreateRequest, OrderResponse, OrderUpdateRequest, PyObjectId


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=OrderResponse)
async def post_order_handler(request: OrderCreateRequest):
    # userId will eventually be moved out of the request body
    new_id = await place_order(request.userId, request)
    return await get_order_by_id(new_id)

@router.get("/", response_model=list[OrderResponse])
async def get_orders_handler():
    return await get_orders()

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_handler(order_id: PyObjectId):
    order = await get_order_by_id(order_id)
    if order:
        return order
    raise OrderNotFoundException()

@router.patch("/{order_id}", response_model=OrderResponse)
async def patch_order_handler(order_id: PyObjectId, request: OrderUpdateRequest):
    updated_order = await update_order(order_id, request)
    if updated_order:
        return updated_order
    raise OrderNotFoundException()
