from datetime import datetime, timedelta, timezone

from dotenv import dotenv_values
from fastapi import APIRouter, Depends
from fastapi.exceptions import ValidationException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext

# This definition must go here, otherwise the app crashes from circular import. (main->security->crud.get_user_by_username->security.create_hashed_password)
CONFIG = dotenv_values("/code/app/.env")
MAXIMUM_JWT_LIFETIME = timedelta(hours=12)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes={"user":"basic user access", "kitchen":"access to menuitems", "admin":"control over users and kitchens", "superadmin":"full control"})

def create_hashed_password(password) -> str:
    """Make a new password hash for the passed password"""
    return pwd_context.hash(password)

def verify_password(entered_password, hashed_password) -> bool:
    """Verify the entered password matches the hashed password"""
    return pwd_context.verify(entered_password, hashed_password)

from .crud import get_user_by_username
from .exceptions import CredentialsException, FailedLoginException, ScopeSelectionException, UnauthorizedUserException
from .schemas import Token, TokenData


def create_access_token(data: dict) -> str:
    expires_delta = timedelta(minutes=float(CONFIG["JWT_LIFETIME_MINUTES"]))
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + min(expires_delta,MAXIMUM_JWT_LIFETIME)
    encoded_jwt = jwt.encode(to_encode, CONFIG["JWT_SECRET_KEY"], algorithm=CONFIG["JWT_ALGORITHM"])
    return encoded_jwt

async def authenticate_password(username: str, password: str) -> dict:
    """Attempt to authenticate using the given username and password"""
    user = await get_user_by_username(username)
    if not user:
        raise FailedLoginException()
    if not verify_password(password, user["hashed_password"]):
        raise FailedLoginException()
    return user

def authenticate_jwt(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Attempt to authenticate using the given JWT"""
    try:
        payload = jwt.decode(token, CONFIG["JWT_SECRET_KEY"], algorithms=[CONFIG["JWT_ALGORITHM"]])
        token_data = TokenData(**payload)
    except (JWTError, ValidationException):
        raise CredentialsException()
    return token_data


router = APIRouter(
    tags=["Security"]
)

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = await authenticate_password(form_data.username, form_data.password)
    if len(form_data.scopes[0])!=1:
        raise ScopeSelectionException()
    desired_role = form_data.scopes[0]
    if desired_role not in user["roles"]:
        raise UnauthorizedUserException()
    # The create_access_token func will generate the correct exp time
    access_token = create_access_token({"sub":str(user["_id"]), "username":user["username"], "role":desired_role})
    return Token(access_token=access_token, token_type="bearer")
