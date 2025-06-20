from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    email: str
    full_name: str
    university: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    domain: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    category_id: int
    condition: str
    
class ProductCreate(ProductBase):
    image_url: str
    seller_id: int

class Product(ProductBase):
    id: int
    image_url: Optional[str]
    created_at: datetime
    is_sold: int
    seller_id: int
    
    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    content: str
    product_id: Optional[int] = None

class Message(MessageCreate):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True