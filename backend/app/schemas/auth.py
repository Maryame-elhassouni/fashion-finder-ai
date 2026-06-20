from pydantic import BaseModel, EmailStr, Field , ConfigDict
from datetime import datetime

class UserRegister(BaseModel):
    email:     EmailStr
    full_name: str = Field(..., min_length=2, max_length=200)
    password:  str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email:    EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:        int
    email:     str
    full_name: str | None
    is_active: bool
    

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserResponse

class UserUpdate(BaseModel):
    full_name:        str | None = Field(None, min_length=2, max_length=200)
    current_password: str | None = Field(None, min_length=6)
    new_password:     str | None = Field(None, min_length=6)

class UserStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user:           UserResponse
    total_searches: int
    last_search_at: datetime | None

    