from bson import ObjectId
from pydantic import BaseModel, Field, field_serializer
from pydantic_core import core_schema

from datetime import datetime
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
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)


# Sub-models for later objects
class OptionsSchema(BaseModel):
    type: str
    choices: list[str] = []

class MenuItemSchema(BaseModel):
    name: str
    price: float
    options: list[OptionsSchema]

class OrderItemSchema(BaseModel):
    kitchenName: str
    name: str
    price: float
    choices: list[str]


# Schemas for item operations
    
# Used for POST and PUT
class ItemCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None

# Used for GET
class ItemResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    @field_serializer('id')
    def serialize_id(self, id: PyObjectId, _info):
        return str(id)
    name: str
    description: Optional[str] = None

# No id field here since it is given by the path
# Used for PATCH
class ItemUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class OrderCreateRequest(BaseModel):
    userId: PyObjectId
    orderItems: list[OrderItemSchema]
    status: str

class OrderResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    @field_serializer('id')
    def serialize_id(self, id: PyObjectId, _info):
        return str(id)
    userId: PyObjectId
    dateOrdered: datetime
    orderItems: list[OrderItemSchema]
    status: str

# Only thing that can be updated is the status
class OrderUpdateRequest(BaseModel):
    status: str

class MenuCreateRequest(BaseModel):
    menuName: str
    kitchenName: str
    menuItems: list[MenuItemSchema]

class MenuResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    @field_serializer('id')
    def serialize_id(self, id: PyObjectId, _info):
        return str(id)
    menuName: str
    kitchenName: str
    menuItems: list[MenuItemSchema]

# Only thing that can be updated is the status
class MenuUpdateRequest(BaseModel):
    menuName: Optional[str] = None
    kitchenName: Optional[str] = None
    menuItems: Optional[list[MenuItemSchema]] = None

class UserCreateRequest(BaseModel):
    username: str
    balance: float

class UserResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    @field_serializer('id')
    def serialize_id(self, id: PyObjectId, _info):
        return str(id)
    username: str
    balance: float

# Only thing that can be updated is the status
class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    balance: Optional[float] = None
