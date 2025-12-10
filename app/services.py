from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from pymongo.collection import Collection
from app.database import db_connection
from app.models import Organization, Admin
from app.auth import auth_service


class OrganizationService:
    """Service class for organization-related database operations"""
    
    def __init__(self):
        self.master_db = db_connection.get_master_db()
        self.organizations_collection: Collection = db_connection.get_collection("organizations")
        self.admins_collection: Collection = db_connection.get_collection("admins")
    
    def _generate_collection_name(self, organization_name: str) -> str:
        """Generate a collection name for an organization"""
        # Sanitize organization name for collection naming
        sanitized_name = organization_name.lower().replace(" ", "_").replace("-", "_")
        return f"org_{sanitized_name}"
    
    def organization_exists(self, organization_name: str) -> bool:
        """Check if an organization with the given name exists"""
        result = self.organizations_collection.find_one({"organization_name": organization_name})
        return result is not None
    
    def email_exists(self, email: str) -> bool:
        """Check if an admin with the given email exists"""
        result = self.admins_collection.find_one({"email": email})
        return result is not None
    
    def create_organization(
        self, 
        organization_name: str, 
        email: str, 
        password: str
    ) -> Organization:
        """Create a new organization with an admin user"""
        
        # Generate collection name
        collection_name = self._generate_collection_name(organization_name)
        
        # Hash the password
        hashed_password = auth_service.get_password_hash(password)
        
        # Create organization document
        org_data = {
            "organization_name": organization_name,
            "collection_name": collection_name,
            "admin_id": None,  # Will be updated after admin creation
            "admin_email": email,
            "created_at": datetime.utcnow(),
            "updated_at": None
        }
        
        # Insert organization
        org_result = self.organizations_collection.insert_one(org_data)
        organization_id = str(org_result.inserted_id)
        
        # Create admin user
        admin_data = {
            "email": email,
            "hashed_password": hashed_password,
            "organization_id": organization_id,
            "created_at": datetime.utcnow()
        }
        
        # Insert admin
        admin_result = self.admins_collection.insert_one(admin_data)
        admin_id = str(admin_result.inserted_id)
        
        # Update organization with admin_id
        self.organizations_collection.update_one(
            {"_id": org_result.inserted_id},
            {"$set": {"admin_id": admin_id}}
        )
        
        # Create dynamic collection for the organization
        db_connection.create_collection(collection_name)
        
        # Retrieve and return the created organization
        org_doc = self.organizations_collection.find_one({"_id": org_result.inserted_id})
        return Organization.from_dict(org_doc)
    
    def get_organization_by_name(self, organization_name: str) -> Optional[Organization]:
        """Get an organization by name"""
        org_doc = self.organizations_collection.find_one({"organization_name": organization_name})
        if org_doc:
            return Organization.from_dict(org_doc)
        return None
    
    def get_organization_by_id(self, organization_id: str) -> Optional[Organization]:
        """Get an organization by ID"""
        try:
            org_doc = self.organizations_collection.find_one({"_id": ObjectId(organization_id)})
            if org_doc:
                return Organization.from_dict(org_doc)
        except Exception:
            pass
        return None
    
    def update_organization(
        self, 
        old_organization_name: str, 
        new_organization_name: str,
        email: str,
        password: str
    ) -> Optional[Organization]:
        """Update an organization (rename) and sync data to new collection"""
        
        # Get existing organization
        org_doc = self.organizations_collection.find_one({"organization_name": old_organization_name})
        if not org_doc:
            return None
        
        old_collection_name = org_doc["collection_name"]
        new_collection_name = self._generate_collection_name(new_organization_name)
        
        # Get admin and verify credentials
        admin_doc = self.admins_collection.find_one({"_id": ObjectId(org_doc["admin_id"])})
        if not admin_doc or admin_doc["email"] != email:
            return None
        
        # Verify password
        if not auth_service.verify_password(password, admin_doc["hashed_password"]):
            return None
        
        # Create new collection
        db_connection.create_collection(new_collection_name)
        
        # Copy data from old collection to new collection
        old_collection = db_connection.get_collection(old_collection_name)
        new_collection = db_connection.get_collection(new_collection_name)
        
        # Get all documents from old collection
        documents = list(old_collection.find({}))
        if documents:
            new_collection.insert_many(documents)
        
        # Update organization document
        self.organizations_collection.update_one(
            {"_id": org_doc["_id"]},
            {
                "$set": {
                    "organization_name": new_organization_name,
                    "collection_name": new_collection_name,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Drop old collection
        db_connection.drop_collection(old_collection_name)
        
        # Return updated organization
        updated_doc = self.organizations_collection.find_one({"_id": org_doc["_id"]})
        return Organization.from_dict(updated_doc)
    
    def delete_organization(
        self, 
        organization_name: str,
        admin_id: str
    ) -> bool:
        """Delete an organization and its associated collection"""
        
        # Get organization
        org_doc = self.organizations_collection.find_one({"organization_name": organization_name})
        if not org_doc:
            return False
        
        # Verify that the requesting admin owns this organization
        if org_doc["admin_id"] != admin_id:
            return False
        
        collection_name = org_doc["collection_name"]
        
        # Delete organization collection
        db_connection.drop_collection(collection_name)
        
        # Delete admin user
        self.admins_collection.delete_one({"_id": ObjectId(org_doc["admin_id"])})
        
        # Delete organization
        self.organizations_collection.delete_one({"_id": org_doc["_id"]})
        
        return True
    
    def authenticate_admin(self, email: str, password: str) -> Optional[Admin]:
        """Authenticate an admin user"""
        admin_doc = self.admins_collection.find_one({"email": email})
        if not admin_doc:
            return None
        
        # Verify password
        if not auth_service.verify_password(password, admin_doc["hashed_password"]):
            return None
        
        return Admin.from_dict(admin_doc)


# Singleton instance
organization_service = OrganizationService()
