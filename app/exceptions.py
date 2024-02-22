from typing import Any, Dict
from typing_extensions import Annotated, Doc
from fastapi import HTTPException

class EntityNotFoundException(HTTPException):
    def __init__(self, detail="Entity not found"):
        super().__init__(404, detail)

class ChoiceNotFoundException(EntityNotFoundException):
    def __init__(self):
        super().__init__("Choice not found")

class MenuItemNotFoundException(EntityNotFoundException):
    def __init__(self):
        super().__init__("MenuItem not found")

class OrderNotFoundException(EntityNotFoundException):
    def __init__(self):
        super().__init__("Order not found")

class UserNotFoundException(EntityNotFoundException):
    def __init__(self):
        super().__init__("User not found")

class InsufficientBalanceException(HTTPException):
    def __init__(self):
        super().__init__(409, "User has insufficient balance")
