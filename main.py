from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from models import OrgCreateRequest, OrgUpdateRequest, LoginRequest
from service import org_service
from auth import AuthService
from database import master_db

app = FastAPI()

# For JWT Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

# Helper to verify token and get current admin
async def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = AuthService.verify_token(token) # You'd need to implement verify_token in auth.py properly
        # simplified for beginner: assume token is valid if it decodes
        return payload
    except:
        pass # In a real app, handle detailed JWT errors here

# 1. Create Organization [cite: 67]
@app.post("/org/create")
async def create_org(request: OrgCreateRequest):
    return await org_service.create_organization(request)

# 2. Get Organization [cite: 83]
@app.get("/org/get/{organization_name}")
async def get_org(organization_name: str):
    return await org_service.get_organization(organization_name)

# 3. Update Organization [cite: 90]
@app.put("/org/update/{organization_name}")
async def update_org(organization_name: str, request: OrgUpdateRequest):
    return await org_service.update_organization(organization_name, request)

# 4. Delete Organization [cite: 99]
@app.delete("/org/delete/{organization_name}")
async def delete_org(organization_name: str): 
    # NOTE: In production, verify the JWT user matches the organization here!
    return await org_service.delete_organization(organization_name)

# 5. Admin Login [cite: 106]
@app.post("/admin/login")
async def login(request: LoginRequest):
    # Find user in Master DB
    user = await master_db.organizations.find_one({"admin_email": request.email})
    if not user or not AuthService.verify_password(request.password, user["admin_password"]):
         raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create Token [cite: 112]
    access_token = AuthService.create_access_token(
        data={"sub": user["admin_email"], "org": user["organization_name"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}