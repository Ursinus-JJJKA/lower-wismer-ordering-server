from bson import ObjectId
from pydantic import BaseModel, Field, field_serializer
from pydantic_core import core_schema
from typing import Any, Optional

# I'm aware the next lines are confusing and looks bad. This is the result of hours of troubleshooting and searching. Pray it doesn't break
# For reference, here's what I tried after many stack overflow pages:
#     I tried setting pydantic.json. whatever but that doesn't exist and pydantic.Json doesn't have the attribute the solution wanted
#     I tried many variations of defining PyObjectId that worked to seemlessly convert to strings, didn't work for me (til this one)
#     I tried using the pydantic-mongo package and their ObjectId didn't work. I also tried rolling back the version of pydantic to 2.3 which someone reported working

# class PyObjectId(ObjectId):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, value: Any) -> ObjectId:
#         """Validates if the provided value is a valid ObjectId."""
#         if isinstance(value, ObjectId):
#             return value
#         if isinstance(value, str) and ObjectId.is_valid(value):
#             return ObjectId(value)
#         raise ValueError("Invalid ObjectId")

#     @classmethod
#     def __get_pydantic_core_schema__(
#             cls, _source_type: Any, _handler: Any
#     ) -> core_schema.CoreSchema:
#         """
#         Defines the core schema for FastAPI documentation.
#         Creates a JSON schema representation compatible with Pydantic's requirements.
#         """
#         return core_schema.json_or_python_schema(
#             json_schema=core_schema.str_schema(),
#             python_schema=core_schema.is_instance_schema(ObjectId)
#         )

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

# class UserBase(BaseModel):
#     email: str


# class UserCreate(UserBase):
#     password: str


# class User(UserBase):
#     id: int
#     is_active: bool
#     items: list[Item] = []

#     class Config:
#         orm_mode = True