from fastapi import APIRouter, Depends

from ..crud import get_orders, get_order_by_id, get_orders_by_user, place_order, update_order
from ..dependencies import assert_kitchen_access, authenticate_jwt
from ..exceptions import OrderNotFoundException
from ..schemas import OrderCreateRequest, OrderResponse, OrderUpdateRequest, PyObjectId, Role, TokenData


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=OrderResponse, status_code=201)
async def post_order_handler(request: OrderCreateRequest, verified_token_data: TokenData = Depends(authenticate_jwt)):
    new_id = await place_order(verified_token_data.sub, request)
    return await get_order_by_id(new_id)

@router.get("/", response_model=list[OrderResponse])
async def get_orders_handler(verified_token_data: TokenData = Depends(authenticate_jwt)):
    if verified_token_data.role in [Role.superadmin, Role.admin, Role.kitchen]:
        return await get_orders()
    else:
        return await get_orders_by_user(verified_token_data.sub)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_handler(order_id: PyObjectId, verified_token_data: TokenData = Depends(authenticate_jwt)):
    order = await get_order_by_id(order_id)
    requester_is_kitchen_or_admin = verified_token_data.role in [Role.superadmin, Role.admin, Role.kitchen]
    if order and (requester_is_kitchen_or_admin or order["userId"] == verified_token_data.sub):
        return order
    raise OrderNotFoundException()

@router.patch("/{order_id}", response_model=OrderResponse)
async def patch_order_handler(order_id: PyObjectId, request: OrderUpdateRequest, verified_token_data: TokenData = Depends(assert_kitchen_access)):
    updated_order = await update_order(order_id, request)
    if updated_order:
        return updated_order
    raise OrderNotFoundException()
