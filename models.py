from pydantic import BaseModel, EmailStr
from typing import Optional

# Input for Creating an Organization [cite: 68-71]
class OrgCreateRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

# Input for Updating an Organization [cite: 91-95]
class OrgUpdateRequest(BaseModel):
    organization_name: str
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# Input for Admin Login [cite: 107-109]
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Response model for Organization details
class OrgResponse(BaseModel):
    organization_name: str
    collection_name: str
    admin_email: str