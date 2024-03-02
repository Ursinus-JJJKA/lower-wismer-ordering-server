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

class DatabaseViolation(HTTPException):
    def __init__(self, detail="Document validation failed"):
        super().__init__(409, detail)

class InsufficientBalanceException(DatabaseViolation):
    def __init__(self):
        super().__init__("User has insufficient balance")

class IllegalRadioSelectionException(HTTPException):
    def __init__(self):
        super().__init__(400, "Exactly one choice should be selected in a radio group")

class MenuItemNotAvailableException(HTTPException):
    def __init__(self):
        super().__init__(400, "This MenuItem is unavailable at this time")

class OptionsGroupsMismatch(HTTPException):
    def __init__(self):
        super().__init__(400, "The wrong number of groups was passed")