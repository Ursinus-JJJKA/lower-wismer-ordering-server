from datetime import datetime, timedelta, timezone

from dotenv import dotenv_values
from fastapi import Depends
from fastapi.exceptions import ValidationException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from .exceptions import CredentialsException
from .schemas import TokenData


CONFIG = dotenv_values("/run/secrets/env_file")
MAXIMUM_JWT_LIFETIME = timedelta(hours=24)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes={"user":"basic user access", "kitchen":"access to menuitems", "admin":"control over users and kitchens", "superadmin":"full control"})

def create_hashed_password(password: str) -> str:
    """Make a new password hash for the passed password"""
    return pwd_context.hash(password)

def verify_password(entered_password: str, hashed_password: str) -> bool:
    """Verify the entered password matches the hashed password"""
    return pwd_context.verify(entered_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Make a JWT access token and return as a string"""
    lifetime_minutes = CONFIG.get(f"{data["role"].upper()}_JWT_LIFETIME_MINUTES", CONFIG["JWT_LIFETIME_MINUTES"])
    expires_delta = timedelta(minutes=float(lifetime_minutes))
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + min(expires_delta, MAXIMUM_JWT_LIFETIME)
    encoded_jwt = jwt.encode(to_encode, CONFIG["JWT_SECRET_KEY"], algorithm=CONFIG["JWT_ALGORITHM"])
    return encoded_jwt

def authenticate_jwt(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Attempt to authenticate using the given JWT"""
    try:
        payload = jwt.decode(token, CONFIG["JWT_SECRET_KEY"], algorithms=[CONFIG["JWT_ALGORITHM"]])
        token_data = TokenData(**payload)
    except (JWTError, ValidationException):
        raise CredentialsException()
    return token_data
