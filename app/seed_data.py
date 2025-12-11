"""
Database seeding module for initial demo data
"""
from app.services import OrganizationService
from app.database import db_connection
from datetime import datetime


def seed_demo_data():
    """Seed the database with sample organizations and data"""
    try:
        org_service = OrganizationService()
        
        # Sample organizations to create
        sample_orgs = [
            {
                "name": "TechCorp Solutions",
                "email": "admin@techcorp.com",
                "password": "TechCorp@2025"
            },
            {
                "name": "StartUp Hub",
                "email": "admin@startuphub.com",
                "password": "StartUp@2025"
            },
            {
                "name": "Global Enterprises",
                "email": "admin@globalenterprises.com",
                "password": "Global@2025"
            }
        ]
        
        created_orgs = []
        
        for org_data in sample_orgs:
            # Check if org already exists
            if org_service.organization_exists(org_data["name"]):
                print(f"✓ Organization '{org_data['name']}' already exists")
                existing_org = org_service.get_organization_by_name(org_data["name"])
                created_orgs.append({
                    "name": org_data["name"],
                    "email": org_data["email"],
                    "password": org_data["password"],
                    "collection": existing_org.collection_name
                })
                continue
            
            # Create new organization
            org = org_service.create_organization(
                organization_name=org_data["name"],
                email=org_data["email"],
                password=org_data["password"]
            )
            
            # Add sample data to the organization's collection
            org_db = db_connection.get_master_db().client[db_connection.get_master_db().name]
            org_collection = org_db[org.collection_name]
            
            # Insert sample records
            sample_records = [
                {
                    "name": f"Employee 1 - {org.organization_name}",
                    "email": f"emp1@{org.organization_name.lower().replace(' ', '')}.com",
                    "department": "Engineering",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": f"Employee 2 - {org.organization_name}",
                    "email": f"emp2@{org.organization_name.lower().replace(' ', '')}.com",
                    "department": "Marketing",
                    "created_at": datetime.utcnow()
                },
                {
                    "name": f"Employee 3 - {org.organization_name}",
                    "email": f"emp3@{org.organization_name.lower().replace(' ', '')}.com",
                    "department": "Sales",
                    "created_at": datetime.utcnow()
                }
            ]
            
            org_collection.insert_many(sample_records)
            
            created_orgs.append({
                "name": org.organization_name,
                "email": org.admin_email,
                "password": org_data["password"],
                "collection": org.collection_name,
                "status": "created"
            })
            
            print(f"✓ Created organization: {org.organization_name}")
            print(f"  - Collection: {org.collection_name}")
            print(f"  - Admin Email: {org.admin_email}")
            print(f"  - Sample records added: 3 employees")
        
        print("\n" + "="*60)
        print("DEMO DATA CREATED SUCCESSFULLY")
        print("="*60)
        print("\nCredentials for testing:\n")
        
        for org in created_orgs:
            print(f"Organization: {org['name']}")
            print(f"  Email: {org['email']}")
            print(f"  Password: {org['password']}")
            print(f"  Collection: {org['collection']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"Error seeding data: {str(e)}")
        return False


if __name__ == "__main__":
    seed_demo_data()
