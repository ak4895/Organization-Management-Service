from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationGet,
    OrganizationUpdate,
    OrganizationDelete
)
from app.services import organization_service
from app.dependencies import get_current_admin
from app.schemas import TokenData


router = APIRouter(prefix="/org", tags=["Organizations"])


@router.post("/create", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(request: OrganizationCreate):
    """
    Create a new organization with an admin user.
    
    - Validates that the organization name does not already exist
    - Creates a dynamic MongoDB collection for the organization
    - Creates an admin user for the organization
    - Stores metadata in the Master Database
    """
    
    # Check if organization already exists
    if organization_service.organization_exists(request.organization_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization with name '{request.organization_name}' already exists"
        )
    
    # Check if email already exists
    if organization_service.email_exists(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Admin with email '{request.email}' already exists"
        )
    
    try:
        # Create organization
        organization = organization_service.create_organization(
            organization_name=request.organization_name,
            email=request.email,
            password=request.password
        )
        
        # Return response
        return OrganizationResponse(
            organization_id=organization.organization_id,
            organization_name=organization.organization_name,
            collection_name=organization.collection_name,
            admin_email=organization.admin_email,
            created_at=organization.created_at,
            updated_at=organization.updated_at
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating organization: {str(e)}"
        )


@router.get("/get", response_model=OrganizationResponse)
async def get_organization(organization_name: str):
    """
    Get organization details by name.
    
    - Fetches organization metadata from the Master Database
    - Returns 404 if organization does not exist
    """
    
    organization = organization_service.get_organization_by_name(organization_name)
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with name '{organization_name}' not found"
        )
    
    return OrganizationResponse(
        organization_id=organization.organization_id,
        organization_name=organization.organization_name,
        collection_name=organization.collection_name,
        admin_email=organization.admin_email,
        created_at=organization.created_at,
        updated_at=organization.updated_at
    )


@router.put("/update", response_model=OrganizationResponse)
async def update_organization(request: OrganizationUpdate):
    """
    Update an organization (rename).
    
    - Validates admin credentials
    - Creates a new collection with the new name
    - Syncs existing data to the new collection
    - Deletes the old collection
    """
    
    # Check if the new organization name already exists (and it's not the same organization)
    existing_org = organization_service.get_organization_by_name(request.organization_name)
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization with name '{request.organization_name}' already exists"
        )
    
    # Get admin to verify credentials
    admin = organization_service.authenticate_admin(request.email, request.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Get the organization by admin
    old_org = organization_service.get_organization_by_id(admin.organization_id)
    if not old_org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    try:
        # Update organization
        updated_org = organization_service.update_organization(
            old_organization_name=old_org.organization_name,
            new_organization_name=request.organization_name,
            email=request.email,
            password=request.password
        )
        
        if not updated_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update organization"
            )
        
        return OrganizationResponse(
            organization_id=updated_org.organization_id,
            organization_name=updated_org.organization_name,
            collection_name=updated_org.collection_name,
            admin_email=updated_org.admin_email,
            created_at=updated_org.created_at,
            updated_at=updated_org.updated_at
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating organization: {str(e)}"
        )


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    request: OrganizationDelete,
    current_admin: TokenData = Depends(get_current_admin)
):
    """
    Delete an organization.
    
    - Requires authentication
    - Only the admin of the organization can delete it
    - Deletes the organization collection and metadata
    """
    
    # Verify that the organization exists
    organization = organization_service.get_organization_by_name(request.organization_name)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with name '{request.organization_name}' not found"
        )
    
    try:
        # Delete organization
        success = organization_service.delete_organization(
            organization_name=request.organization_name,
            admin_id=current_admin.admin_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this organization"
            )
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting organization: {str(e)}"
        )
