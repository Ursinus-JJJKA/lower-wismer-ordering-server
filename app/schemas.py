from bson import Decimal128, ObjectId
from pydantic import BaseModel, Field
from pydantic_core import core_schema

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional


# I'm aware the next lines are confusing and look bad. This is the result of hours of troubleshooting and searching. Pray it doesn't break
# For reference, here's what I tried after many stack overflow pages:
#     I tried setting pydantic.json. whatever but that doesn't exist anymore and pydantic.Json doesn't have the attribute the solution wanted
#     I tried many variations of defining PyObjectId that worked to seemlessly convert to strings, didn't work for me (til this one)
#     I tried using the pydantic-mongo package and their ObjectId didn't work. I also tried rolling back the version of pydantic to 2.3 which someone reported working
#     I even resorted to walking through the problem with ChatGPT; it kept spitting out stupid responses like "don't return the id field" or try this error ridden, deprecated code
# Many of the changes are breaking thanks to pydantic upgrading to recent versions (half of the suggested code online is now deprecated)

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x),
                when_used="json"
            ),
        )
    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)

class PyDecimal128(Decimal):
    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.decimal_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(Decimal128),
                core_schema.chain_schema([
                    core_schema.decimal_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: float(x.to_decimal()),
                when_used="json"
            ),
        )
    @classmethod
    def validate(cls, value) -> Decimal128:
        return Decimal128(value)

# Sub-models for later objects
    
class OrderStatus(str, Enum):
    ordered = "ordered"
    ready = "ready"
    fulfilled = "fulfilled"

class OptionType(str, Enum):
    radio = "radio"
    checkbox = "checkbox"

class OptionsSchema(BaseModel):
    type: OptionType
    choices: dict[str, PyDecimal128] = {}

class OrderItemSchema(BaseModel):
    menuName: str
    itemName: str
    kitchenName: Optional[str] = None
    price: Optional[PyDecimal128] = None
    choices: list[list[str]]

# Schemas for item operations
# Note that these schemas may diverge from what the database stores

class OrderCreateRequest(BaseModel):
    # Will eventually be removed once the auth system is implemented
    userId: PyObjectId
    orderItems: list[OrderItemSchema]

class OrderResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    userId: PyObjectId
    dateOrdered: datetime
    orderItems: list[OrderItemSchema]
    status: dict[str, OrderStatus]

# Only thing that can be updated is the status
class OrderUpdateRequest(BaseModel):
    status: Optional[dict[str, OrderStatus]] = None

class MenuItemCreateRequest(BaseModel):
    menuName: str
    itemName: str
    kitchenName: str
    price: PyDecimal128
    options: list[OptionsSchema] = []
    available: bool = True

class MenuItemResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    menuName: str
    itemName: str
    kitchenName: str
    price: PyDecimal128
    options: list[OptionsSchema]
    available: bool

class MenuItemUpdateRequest(BaseModel):
    menuName: Optional[str] = None
    itemName: Optional[str] = None
    kitchenName: Optional[str] = None
    price: Optional[PyDecimal128] = None
    options: Optional[list[OptionsSchema]] = None
    available: Optional[bool] = None

class UserCreateRequest(BaseModel):
    username: str
    balance: PyDecimal128

class UserResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    balance: PyDecimal128

# Only thing that can be updated is the status
class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    balance: Optional[PyDecimal128] = None
