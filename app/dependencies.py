from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.auth import auth_service
from app.schemas import TokenData


security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """Dependency to get the current authenticated admin from JWT token"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    token_data = auth_service.decode_access_token(token)
    
    if token_data is None:
        raise credentials_exception
    
    return token_data


async def get_optional_current_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[TokenData]:
    """Optional dependency to get the current admin if authenticated"""
    
    if credentials is None:
        return None
    
    token = credentials.credentials
    token_data = auth_service.decode_access_token(token)
    
    return token_data
