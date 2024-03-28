from datetime import datetime

from pymongo import ReturnDocument

from . import exceptions, schemas
from .database import get_collection, get_session
from .security import create_hashed_password


# These functions should do what they say without worrying about authentication or permissions
# Remember to do checks that the data inserted or modified is valid

async def create_menuitem(request: schemas.MenuItemCreateRequest, *, session=None) -> schemas.ObjectId:
    result = await get_collection("MenuItems").insert_one(request.model_dump(), session=session)
    return result.inserted_id

async def get_menuitem_by_id(_id: schemas.ObjectId, *, session=None) -> dict:
    return await get_collection("MenuItems").find_one({"_id": _id}, session=session)

async def get_menuitem_by_names(menuName: str, itemName: str, *, session=None) -> dict:
    return await get_collection("MenuItems").find_one({"menuName": menuName, "itemName": itemName}, session=session)

async def get_menuitems(*, session=None) -> list[dict]:
    return await get_collection("MenuItems").find({}, session=session).to_list(length=None)

async def get_menuitems_by_menu(menuName: str, *, session=None) -> list[dict]:
    return await get_collection("MenuItems").find({"menuName": menuName}, session=session).to_list(length=None)

async def get_menunames(*, session=None) -> list[str]:
    return await get_collection("MenuItems").distinct("menuName", session=session)

async def get_kitchennames(*, session=None) -> list[str]:
    return await get_collection("MenuItems").distinct("kitchenName", session=session)

async def update_menuitem(_id: schemas.ObjectId, request: schemas.MenuItemUpdateRequest, *, session=None) -> dict:
    return await get_collection("MenuItems").find_one_and_update(
        {"_id": _id}, {"$set": request.model_dump(exclude_unset=True)},
        return_document=ReturnDocument.AFTER, session=session
    )

async def delete_menuitem(_id: schemas.ObjectId, *, session=None) -> dict:
    return await get_collection("MenuItems").find_one_and_delete({"_id": _id}, session=session)


def _calculate_total_price(orderItems: list[schemas.OrderItemSchema]) -> schemas.Decimal:
    # The order items coming in should be valid, aka the choices have been included into the item
    return sum(item.price.to_decimal() for item in orderItems)

def _validated_choices(passed_groups: list[list[str]], menuItem: dict) -> tuple[list[str],schemas.Decimal]:
    choices_extra_cost = schemas.Decimal()
    if len(passed_groups) != len(menuItem["options"]):
        raise exceptions.OptionsGroupsMismatchException()
    # Loop through each group of selections and group of available choices in parallel
    for passed_group_selections,optionGroup in zip(passed_groups,menuItem["options"],strict=True):
        optionType = optionGroup["type"]
        optionChoices = optionGroup["choices"]
        # If you violate the radio condition, raise error
        if optionType==schemas.OptionType.radio and len(passed_group_selections)!=1:
            raise exceptions.IllegalRadioSelectionException()
        # For each selected choice, verify it is available and add the extra cost to the accumulator
        for passed_choice in passed_group_selections:
            if passed_choice not in optionChoices:
                raise exceptions.ChoiceNotFoundException()
            choices_extra_cost += optionChoices[passed_choice].to_decimal()
    # Return the groups (now that are validated) and the extra cost of the choices
    return passed_groups,choices_extra_cost

async def _validated_orderitem(orderItem: schemas.OrderItemSchema, *, session=None) -> schemas.OrderItemSchema:
    #TODO consider throwing if price doesn't match (requires making price a required field in the schema)
    # Verify the requested MenuItem exists and is available
    menuItem = await get_menuitem_by_names(orderItem.menuName, orderItem.itemName, session=session)
    if menuItem is None:
        raise exceptions.MenuItemNotFoundException()
    elif not menuItem["available"]:
        raise exceptions.MenuItemNotAvailableException()
    
    # Check the selected choices and get their cost
    validated_choices,choices_cost = _validated_choices(orderItem.choices, menuItem)
    return schemas.OrderItemSchema(
        menuName=menuItem["menuName"],
        itemName=menuItem["itemName"],
        kitchenName=menuItem["kitchenName"],
        price=menuItem["price"].to_decimal()+choices_cost,
        choices=validated_choices
    )

async def place_order(user_id: schemas.ObjectId, request: schemas.OrderCreateRequest, *, session=None) -> schemas.ObjectId:
    # Try to find user, raise a 404 error if not
    user = await get_user_by_id(user_id, session=session)
    if user is None:
        raise exceptions.UserNotFoundException()
    
    # Get a validated list of items and make a list of kitchens that will need to make the order
    validated_items = [await _validated_orderitem(o, session=session) for o in request.orderItems]
    kitchens = set(item.kitchenName for item in validated_items)

    # Get the total price and verify that the user can pay for it
    total_price = _calculate_total_price(validated_items)
    if total_price > user["balance"].to_decimal():
        raise exceptions.InsufficientBalanceException()
    
    # Make user pay for it
    await get_collection("Users").update_one({"_id": user_id}, {"$inc": {"balance": schemas.Decimal128(-total_price)}}, session=session)
    try:
        # Place the order in the database
        data = {
            "userId": user_id,
            "dateOrdered": datetime.now(),
            "orderItems": [item.model_dump() for item in validated_items],
            "status": dict.fromkeys(kitchens, schemas.OrderStatus.ordered)
        }
        result = await get_collection("Orders").insert_one(data, session=session)
        return result.inserted_id
    except:
        # If something fails, refund the user
        await get_collection("Users").update_one({"_id": user_id}, {"$inc": {"balance": schemas.Decimal128(total_price)}}, session=session)
        raise

async def get_orders(*, session=None) -> list[dict]:
    return await get_collection("Orders").find({}, session=session).to_list(length=None)

async def get_orders_by_user(user_id: schemas.ObjectId, *, session=None) -> list[dict]:
    return await get_collection("Orders").find({"userId": user_id}, session=session).to_list(length=None)

async def get_order_by_id(_id: schemas.ObjectId, *, session=None) -> dict:
    return await get_collection("Orders").find_one({"_id": _id}, session=session)

async def get_active_orders_by_kitchen(kitchenName: str, *, session=None) -> list[dict]:
    return await get_collection("Orders").find({f"status.{kitchenName}": {"$in": ["ordered", "ready"]}}, session=session).to_list(length=None)

#TODO investigate if an injection attack is possible here
async def update_order(_id: schemas.ObjectId, request: schemas.OrderUpdateRequest, *, session=None) -> dict:
    # Formatting so that updates to status object works
    update_data = request.model_dump(exclude_unset=True)
    status_update = update_data["status"]
    del update_data["status"]
    for kitchenname,val in status_update.items():
        update_data[f"status.{kitchenname}"] = val

    return await get_collection("Orders").find_one_and_update(
        {"_id": _id}, {"$set": update_data},
        return_document=ReturnDocument.AFTER, session=session
    )


async def create_user(request: schemas.UserCreateRequest, *, session=None) -> schemas.ObjectId:
    new_user_data = request.model_dump(exclude={"password"})
    new_user_data["hashed_password"] = create_hashed_password(request.password)
    result = await get_collection("Users").insert_one(new_user_data, session=session)
    return result.inserted_id

async def get_user_by_id(_id: schemas.ObjectId, *, session=None) -> dict:
    return await get_collection("Users").find_one({"_id": _id}, session=session)

async def get_user_by_username(username: str, *, session=None) -> dict:
    return await get_collection("Users").find_one({"username": username}, session=session)

async def get_users(*, session=None) -> list[dict]:
    return await get_collection("Users").find({}, session=session).to_list(length=None)

async def update_user(_id: schemas.ObjectId, request: schemas.UserUpdateRequest, *, session=None) -> dict:
    new_user_data = request.model_dump(exclude_unset=True, exclude={"password"})
    if request.password:
        new_user_data["hashed_password"] = create_hashed_password(request.password)
    return await get_collection("Users").find_one_and_update(
        {"_id": _id}, {"$set": new_user_data},
        return_document=ReturnDocument.AFTER, session=session
    )

async def delete_user(_id: schemas.ObjectId, *, session=None) -> dict:
    return await get_collection("Users").find_one_and_delete({"_id": _id}, session=session)
