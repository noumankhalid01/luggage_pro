from pydantic import BaseModel, EmailStr

class CreateUserRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    cnic_image_url: str
    fcm_token: str

class CreateUserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    cnic_image_url: str
    fcm_token: str
    status: str