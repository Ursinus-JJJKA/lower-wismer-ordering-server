from . import exceptions, schemas
from .database import get_collection, get_session

from datetime import datetime
from functools import reduce


# These functions should do what they say without worrying about authentication or permissions
# Remember to do checks that the data inserted or modified is valid

async def create_menuitem(request: schemas.MenuItemCreateRequest, *, session=None) -> schemas.ObjectId:
    #TODO assert unique identifier and nonnegative price
    result = await get_collection("MenuItems").insert_one(request.model_dump(), session=session)
    return result.inserted_id

async def get_menuitem_by_id(_id: schemas.ObjectId, *, session=None) -> dict:
    return await get_collection("MenuItems").find_one({"_id": _id}, session=session)

async def get_menuitem_by_names(menuName: str, itemName: str, *, session=None) -> dict:
    return await get_collection("MenuItems").find_one({"menuName": menuName, "itemName": itemName}, session=session)

async def get_menuitems(*, session=None) -> list:
    return await get_collection("MenuItems").find({}, session=session).to_list(length=None)

async def get_menunames(*, session=None) -> list[str]:
    return await get_collection("MenuItems").distinct("menuName", session=session)

async def get_kitchennames(*, session=None) -> list[str]:
    return await get_collection("MenuItems").distinct("kitchenName", session=session)

async def update_menuitem(_id: schemas.ObjectId, request: schemas.MenuItemUpdateRequest, *, session=None):
    #TODO assert unique identifier and nonnegative price
    return await get_collection("MenuItems").find_one_and_update(
        {"_id": _id}, {"$set": request.model_dump(exclude_unset=True)}, session=session
    )

async def delete_menuitem(_id: schemas.ObjectId, *, session=None):
    return await get_collection("MenuItems").find_one_and_delete({"_id": _id}, session=session)


def _calculate_total_price(order_items) -> float:
    #TODO update to add in choice prices once the schema supports it
    return sum(item.price for item in order_items)

def _validated_choices(passed_choices: list[str], menuItem: dict) -> list[str]:
    #TODO improve this
    available_options = reduce(lambda a,b: a.union(b), [d["choices"] for d in menuItem["options"]], set())
    if any(c not in available_options for c in passed_choices):
        raise exceptions.ChoiceNotFoundException()
    return passed_choices

async def _validated_orderitem(orderItem: schemas.OrderItemSchema, *, session=None) -> schemas.OrderItemSchema:
    menuItem = await get_menuitem_by_names(orderItem.menuName, orderItem.itemName, session=session)
    if menuItem is None:
        raise exceptions.MenuItemNotFoundException()
    
    validated_choices = _validated_choices(orderItem.choices, menuItem)
    return schemas.OrderItemSchema(menuName=menuItem["menuName"], itemName=menuItem["itemName"], kitchenName=menuItem["kitchenName"], price=menuItem["price"], choices=validated_choices)

async def place_order(userId: schemas.ObjectId, request: schemas.OrderCreateRequest, *, session=None) -> schemas.ObjectId:
    user = await get_user_by_id(userId, session=session)
    if user is None:
        raise exceptions.UserNotFoundException()
    
    validated_items = [await _validated_orderitem(o, session=session) for o in request.orderItems]

    total_price = _calculate_total_price(validated_items)
    if total_price > user["balance"]:
        raise exceptions.InsufficientBalanceException()
    
    try:
        await get_collection("Users").update_one({"_id": userId}, {"$inc": {"balance": -total_price}}, session=session)

        data = {"userId": userId, "dateOrdered": datetime.now(),
                "orderItems": [item.model_dump() for item in validated_items], "status": schemas.OrderStatus.ordered}
        result = await get_collection("Orders").insert_one(data, session=session)
        return result.inserted_id
    except:
        await get_collection("Users").replace_one({"_id": userId}, user, session=session)
        raise

async def get_orders(*, session=None) -> list:
    return await get_collection("Orders").find({}, session=session).to_list(length=None)

async def get_orders_by_user(userId: schemas.ObjectId, *, session=None) -> list:
    return await get_collection("Orders").find({"userId": userId}, session=session).to_list(length=None)

async def get_order_by_id(_id: schemas.ObjectId, *, session=None) -> dict:
    return await get_collection("Orders").find_one({"_id": _id}, session=session)

async def update_order(_id: schemas.ObjectId, request: schemas.OrderUpdateRequest, *, session=None):
    #TODO add logic about what transitions are allowed
    return await get_collection("Orders").find_one_and_update(
        {"_id": _id}, {"$set": request.model_dump(exclude_unset=True)}, session=session
    )


async def create_user(request: schemas.UserCreateRequest, *, session=None) -> schemas.ObjectId:
    #TODO assert unique username and nonnegative balance
    result = await get_collection("Users").insert_one(request.model_dump(), session=session)
    return result.inserted_id

async def get_user_by_id(_id: schemas.ObjectId, *, session=None) -> dict:
    return await get_collection("Users").find_one({"_id": _id}, session=session)

async def get_user_by_username(username: str, *, session=None) -> dict:
    return await get_collection("Users").find_one({"username": username}, session=session)

async def get_users(*, session=None) -> list:
    return await get_collection("Users").find({}, session=session).to_list(length=None)

async def update_user(_id: schemas.ObjectId, request: schemas.UserUpdateRequest, *, session=None):
    #TODO assert unique username
    #TODO assert nonnegative balance
    return await get_collection("Users").find_one_and_update(
        {"_id": _id}, {"$set": request.model_dump(exclude_unset=True)}, session=session
    )

async def delete_user(_id: schemas.ObjectId, *, session=None):
    return await get_collection("Users").find_one_and_delete({"_id": _id}, session=session)
