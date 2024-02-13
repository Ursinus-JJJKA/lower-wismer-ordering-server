from fastapi import APIRouter, HTTPException

from ..database import get_collection
from ..schemas import datetime, OrderCreateRequest, OrderResponse, OrderUpdateRequest, PyObjectId


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=OrderResponse)
async def post_order_handler(order: OrderCreateRequest):
    result = await get_collection("orders").insert_one({**order.model_dump(), "dateOrdered": datetime.now()})
    return OrderResponse(**order.model_dump(),_id=result.inserted_id)

@router.get("/", response_model=list[OrderResponse])
async def get_orders_handler():
    return await get_collection("orders").find({}).to_list(length=None)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_handler(order_id: PyObjectId):
    order = await get_collection("orders").find_one({"_id": order_id})
    if order:
        return order
    raise HTTPException(status_code=404, detail=f"Order not found")

async def general_update_order_handler(order_id: PyObjectId, order: OrderCreateRequest, exclude_unset):
    updated_order = await get_collection("orders").find_one_and_update(
        {"_id": order_id}, {"$set": order.model_dump(exclude_unset=exclude_unset)}
    )
    if updated_order:
        return await get_order_handler(order_id)
    raise HTTPException(status_code=404, detail="Order not found")

@router.patch("/{order_id}", response_model=OrderResponse)
async def patch_order_handler(order_id: PyObjectId, order: OrderUpdateRequest):
    return await general_update_order_handler(order_id, order, exclude_unset=True)

@router.delete("/{order_id}", response_model=OrderResponse)
async def delete_order_handler(order_id: PyObjectId):
    deleted_order = await get_collection("orders").find_one_and_delete({"_id": order_id})
    if deleted_order:
        return deleted_order
    raise HTTPException(status_code=404, detail="Order not found")