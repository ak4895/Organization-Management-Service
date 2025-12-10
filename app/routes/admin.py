from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from app.schemas import AdminLoginRequest, AdminLoginResponse
from app.services import organization_service
from app.auth import auth_service
from app.config import settings


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest):
    """
    Authenticate an admin user and return a JWT token.
    
    - Validates admin credentials
    - Returns JWT token containing admin ID and organization ID
    - Token can be used for authenticated endpoints
    """
    
    # Authenticate admin
    admin = organization_service.authenticate_admin(request.email, request.password)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get organization details
    organization = organization_service.get_organization_by_id(admin.organization_id)
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={
            "admin_id": admin.admin_id,
            "organization_id": admin.organization_id,
            "email": admin.email
        },
        expires_delta=access_token_expires
    )
    
    return AdminLoginResponse(
        access_token=access_token,
        token_type="bearer",
        admin_id=admin.admin_id,
        organization_id=organization.organization_id,
        organization_name=organization.organization_name
    )
