from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware  # <--- IMPORT THIS
from fastapi.responses import FileResponse # <--- IMPORT THIS
from models import OrgCreateRequest, OrgUpdateRequest, LoginRequest
from service import org_service
from auth import AuthService
from database import master_db

app = FastAPI()

# --- 🟢 THIS IS THE FIX FOR "CONNECTION ERROR" ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ALL frontends to connect
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],
)
# ------------------------------------------------

# For JWT Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

# Serve the Frontend HTML
@app.get("/")
async def read_root():
    return FileResponse("index.html")

# 1. Create Organization
@app.post("/org/create")
async def create_org(request: OrgCreateRequest):
    return await org_service.create_organization(request)

# 2. Get Organization
@app.get("/org/get/{organization_name}")
async def get_org(organization_name: str):
    return await org_service.get_organization(organization_name)

# 3. Update Organization
@app.put("/org/update/{organization_name}")
async def update_org(organization_name: str, request: OrgUpdateRequest):
    return await org_service.update_organization(organization_name, request)

# 4. Delete Organization
@app.delete("/org/delete/{organization_name}")
async def delete_org(organization_name: str): 
    return await org_service.delete_organization(organization_name)

# 5. Admin Login
@app.post("/admin/login")
async def login(request: LoginRequest):
    user = await master_db.organizations.find_one({"admin_email": request.email})
    if not user or not AuthService.verify_password(request.password, user["admin_password"]):
         raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = AuthService.create_access_token(
        data={"sub": user["admin_email"], "org": user["organization_name"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}