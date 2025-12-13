from database import master_db, client
from auth import AuthService
from models import OrgCreateRequest, OrgUpdateRequest
from fastapi import HTTPException

class OrganizationService:
    
    # 1. Create Organization Logic [cite: 67-82]
    async def create_organization(self, data: OrgCreateRequest):
        # Check if org exists
        existing = await master_db.organizations.find_one({"organization_name": data.organization_name})
        if existing:
            raise HTTPException(status_code=400, detail="Organization name already exists")

        # Dynamic Collection Name [cite: 75]
        collection_name = f"org_{data.organization_name}"
        
        # Hash Password [cite: 128]
        hashed_password = AuthService.get_password_hash(data.password)

        # Prepare Metadata for Master DB [cite: 77-81]
        org_metadata = {
            "organization_name": data.organization_name,
            "collection_name": collection_name,
            "admin_email": data.email,
            "admin_password": hashed_password
        }

        # Save to Master DB
        await master_db.organizations.insert_one(org_metadata)

        # DYNAMIC COLLECTION CREATION [cite: 74, 124]
        # MongoDB creates collections lazily. We insert the admin user to "create" it.
        org_db = client[collection_name] # Access dynamic database/collection
        await org_db.users.insert_one({
            "email": data.email,
            "role": "admin",
            "created_at": "now"
        })

        return {"message": "Organization created successfully", "details": org_metadata}

    # 2. Get Organization Logic [cite: 83-89]
    async def get_organization(self, name: str):
        org = await master_db.organizations.find_one({"organization_name": name})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Convert ObjectId to string for JSON compatibility
        org["_id"] = str(org["_id"])
        return org

    # 3. Update Organization Logic (The Hard Part!) [cite: 90-98]
    async def update_organization(self, current_name: str, data: OrgUpdateRequest):
        org = await master_db.organizations.find_one({"organization_name": current_name})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        update_data = {}
        if data.password:
            update_data["admin_password"] = AuthService.get_password_hash(data.password)
        if data.email:
            update_data["admin_email"] = data.email

        # If name changes, we must MIGRATE DATA [cite: 98]
        if data.organization_name and data.organization_name != current_name:
            # Check if new name is taken
            if await master_db.organizations.find_one({"organization_name": data.organization_name}):
                raise HTTPException(status_code=400, detail="New organization name already exists")

            old_coll_name = org["collection_name"]
            new_coll_name = f"org_{data.organization_name}"

            # 1. Create new collection & Move data
            old_data = await client[old_coll_name].users.find().to_list(length=100)
            if old_data:
                await client[new_coll_name].users.insert_many(old_data)
            
            # 2. Drop old collection
            await client.drop_database(old_coll_name) # Assuming DB per tenant approach or drop_collection

            update_data["organization_name"] = data.organization_name
            update_data["collection_name"] = new_coll_name

        # Update Master DB
        if update_data:
            await master_db.organizations.update_one(
                {"organization_name": current_name}, 
                {"$set": update_data}
            )

        return {"message": "Organization updated successfully"}

    # 4. Delete Organization Logic [cite: 99-105]
    async def delete_organization(self, name: str):
        org = await master_db.organizations.find_one({"organization_name": name})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Delete the Dynamic Collection/DB [cite: 105]
        collection_name = org["collection_name"]
        await client.drop_database(collection_name) # Using drop_database to be clean

        # Delete from Master DB
        await master_db.organizations.delete_one({"organization_name": name})
        return {"message": f"Organization {name} and its data deleted"}

# Create a single instance to use in routes
org_service = OrganizationService()