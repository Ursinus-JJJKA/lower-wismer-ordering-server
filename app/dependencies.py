from fastapi import Depends

from .crud import get_user_by_id
from .exceptions import CredentialsException, UnauthorizedUserException
from .schemas import Role, TokenData
from .security import authenticate_jwt


async def get_current_user(verified_token_data: TokenData = Depends(authenticate_jwt)) -> dict:
    """Get the user that owns the JWT"""
    user = await get_user_by_id(verified_token_data.sub)
    if user is None:
        raise CredentialsException()
    return user

def assert_superadmin_access(verified_token_data: TokenData = Depends(authenticate_jwt)) -> TokenData:
    """Assert the user has superadmin access"""
    if verified_token_data.role not in [Role.superadmin]:
        raise UnauthorizedUserException()
    return verified_token_data

def assert_admin_access(verified_token_data: TokenData = Depends(authenticate_jwt)) -> TokenData:
    """Assert the user has admin access"""
    if verified_token_data.role not in [Role.superadmin, Role.admin]:
        raise UnauthorizedUserException()
    return verified_token_data
    
def assert_kitchen_access(verified_token_data: TokenData = Depends(authenticate_jwt)) -> TokenData:
    """Assert the user has kitchen access"""
    if verified_token_data.role not in [Role.superadmin, Role.admin, Role.kitchen]:
        raise UnauthorizedUserException()
    return verified_token_data

def assert_user_access(verified_token_data: TokenData = Depends(authenticate_jwt)) -> TokenData:
    """Assert the user has (basic) user access"""
    if verified_token_data.role not in [Role.superadmin, Role.admin, Role.kitchen, Role.user]:
        raise UnauthorizedUserException()
    return verified_token_data
