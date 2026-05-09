from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    fcm_token: str

class JWTToken(BaseModel):
    access_token: str
    refresh_token: str

class LoginResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str
    cnic_image_url: str
    status: str
    jwt: JWTToken