from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from typing import List
import enum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String)
    university = Column(String)
    domain = Column(String, index=True, nullable=True)
    google_id = Column(String, unique=True, nullable=True)
    picture = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    products = relationship("Product", back_populates="seller")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    
    products = relationship("Product", back_populates="category")

class ConditionEnum(str, enum.Enum):
    new = "New"
    like_new = "Like New"
    good = "Good"
    fair = "Fair"
    poor = "Poor"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    condition = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_sold = Column(Integer, default=0)
    
    category_id = Column(Integer, ForeignKey("categories.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))
    
    category = relationship("Category", back_populates="products")
    seller = relationship("User", back_populates="products")
    messages = relationship("Message", back_populates="product")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
    product = relationship("Product", back_populates="messages")

# Database operations
def get_user(db, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db, user):
    domain = None
    if '@' in user.email:
        domain = user.email.split('@')[1]
        
    db_user = User(
        email=user.email,
        hashed_password=user.password,
        full_name=user.full_name,
        university=user.university,
        domain=domain
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_product(db, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(db, skip: int = 0, limit: int = 100):
    return db.query(Product).filter(Product.is_sold == 0).offset(skip).limit(limit).all()

def get_products_by_category(db, category_id: int):
    return db.query(Product).filter(Product.category_id == category_id, Product.is_sold == 0).all()

def get_user_products(db, user_id: int):
    return db.query(Product).filter(Product.seller_id == user_id).all()

def create_product(db, product):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product_sold_status(db, product_id: int, is_sold: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.is_sold = is_sold
        db.commit()
        db.refresh(product)
    return product

def get_category(db, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()

def get_categories(db):
    return db.query(Category).all()

def create_message(db, message):
    db_message = Message(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_user_conversations(db, user_id: int):
    sent = db.query(Message).filter(Message.sender_id == user_id).all()
    received = db.query(Message).filter(Message.receiver_id == user_id).all()
    
    # Get unique conversations
    conversations = {}
    for message in sent + received:
        other_user_id = message.receiver_id if message.sender_id == user_id else message.sender_id
        if other_user_id not in conversations:
            conversations[other_user_id] = {
                'user': get_user(db, other_user_id),
                'last_message': message
            }
        elif message.created_at > conversations[other_user_id]['last_message'].created_at:
            conversations[other_user_id]['last_message'] = message
    
    return conversations

def get_chat_messages(db, user1_id: int, user2_id: int, limit: int = 50):
    """Get chat messages between two users."""
    return db.query(Message).filter(
        ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
        ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
    ).order_by(Message.created_at.asc()).limit(limit).all()

def search_products(db, query: str):
    return db.query(Product).filter(
        Product.name.ilike(f"%{query}%") | 
        Product.description.ilike(f"%{query}%"),
        Product.is_sold == 0
    ).all()

def get_users_by_domain(db, domain: str, skip: int = 0, limit: int = 100):
    """Get users from the same domain (community)"""
    return db.query(User).filter(User.domain == domain).offset(skip).limit(limit).all()

def get_products_by_domain(db, domain: str, skip: int = 0, limit: int = 100):
    """Get products from users of the same domain (community)"""
    return db.query(Product).join(User).filter(
        User.domain == domain,
        Product.is_sold == 0
    ).offset(skip).limit(limit).all()