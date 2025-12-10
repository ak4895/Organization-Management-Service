from datetime import datetime
from typing import Optional


class Organization:
    """Organization model for Master Database"""
    
    def __init__(
        self,
        organization_name: str,
        collection_name: str,
        admin_id: str,
        admin_email: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        organization_id: Optional[str] = None
    ):
        self.organization_name = organization_name
        self.collection_name = collection_name
        self.admin_id = admin_id
        self.admin_email = admin_email
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at
        self.organization_id = organization_id
    
    def to_dict(self) -> dict:
        """Convert organization to dictionary"""
        return {
            "organization_name": self.organization_name,
            "collection_name": self.collection_name,
            "admin_id": self.admin_id,
            "admin_email": self.admin_email,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Organization":
        """Create organization from dictionary"""
        org = cls(
            organization_name=data.get("organization_name"),
            collection_name=data.get("collection_name"),
            admin_id=data.get("admin_id"),
            admin_email=data.get("admin_email"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
        org.organization_id = str(data.get("_id", ""))
        return org


class Admin:
    """Admin model for Master Database"""
    
    def __init__(
        self,
        email: str,
        hashed_password: str,
        organization_id: str,
        created_at: Optional[datetime] = None,
        admin_id: Optional[str] = None
    ):
        self.email = email
        self.hashed_password = hashed_password
        self.organization_id = organization_id
        self.created_at = created_at or datetime.utcnow()
        self.admin_id = admin_id
    
    def to_dict(self) -> dict:
        """Convert admin to dictionary"""
        return {
            "email": self.email,
            "hashed_password": self.hashed_password,
            "organization_id": self.organization_id,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Admin":
        """Create admin from dictionary"""
        admin = cls(
            email=data.get("email"),
            hashed_password=data.get("hashed_password"),
            organization_id=data.get("organization_id"),
            created_at=data.get("created_at")
        )
        admin.admin_id = str(data.get("_id", ""))
        return admin
