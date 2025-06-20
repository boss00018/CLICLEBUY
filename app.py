from fastapi import FastAPI, Request, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Form, UploadFile, File, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exception_handlers import http_exception_handler
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
import uvicorn
import os
import shutil
import json
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext
from rate_limiter import RateLimiter
from starlette.middleware.sessions import SessionMiddleware
from google_auth import oauth, create_google_user, extract_domain
from cleanup import cleanup_sold_products, cleanup_orphaned_images
import threading
import time

# Import models and database
from database import SessionLocal, engine
import models
import schemas

# Create tables
models.Base.metadata.create_all(bind=engine)

# JWT settings
SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)  # Generate secure random key if not provided
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="CIRCLEBUY")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Add session middleware for OAuth
app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY
)

# Mount static files
os.makedirs("static/images/products", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Initialize rate limiter
rate_limiter = RateLimiter(requests_per_minute=60)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        # Store connections with user_id as key
        self.active_connections: Dict[int, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f"User {user_id} connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            print(f"User {user_id} disconnected. Remaining connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            print(f"Sending message to user {user_id}")
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)
        else:
            print(f"User {user_id} not connected, cannot send message")

manager = ConnectionManager()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user_from_cookie(
    access_token: Optional[str] = Cookie(None, alias="access_token"),
    db: Session = Depends(get_db)
):
    if not access_token:
        return None
    
    try:
        # Remove "Bearer " prefix if present
        if access_token.startswith("Bearer "):
            access_token = access_token[7:]
            
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = schemas.TokenData(username=username)
    except JWTError:
        return None
    
    user = models.get_user_by_email(db, email=token_data.username)
    return user

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(None, alias="access_token")
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try to get token from cookie if not provided in header
    if not token and access_token:
        if access_token.startswith("Bearer "):
            token = access_token[7:]
        else:
            token = access_token
    
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
        
    user = models.get_user_by_email(db, email=token_data.username)
    if user is None:
        raise credentials_exception
        
    return user

# Error handlers
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url="/login?next=" + request.url.path, status_code=302)
    
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": exc.status_code,
            "error_title": "Error",
            "error_message": exc.detail
        },
        status_code=exc.status_code
    )

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 404,
            "error_title": "Page Not Found",
            "error_message": "The page you're looking for doesn't exist."
        },
        status_code=404
    )

@app.exception_handler(500)
async def server_error_exception_handler(request: Request, exc):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 500,
            "error_title": "Server Error",
            "error_message": "An unexpected error occurred. Please try again later."
        },
        status_code=500
    )

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(get_current_user_from_cookie)):
    products = models.get_products(db, limit=8)
    categories = models.get_categories(db)
    return templates.TemplateResponse("index.html", {"request": request, "products": products, "categories": categories, "current_user": current_user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: Optional[str] = None):
    return templates.TemplateResponse("login.html", {"request": request, "next": next})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    university: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = models.get_user_by_email(db, email=email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(password)
    user = models.create_user(
        db=db,
        user=schemas.UserCreate(
            email=email,
            password=hashed_password,
            full_name=full_name,
            university=university
        )
    )
    
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/token")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    next: Optional[str] = Form(None)
):
    user = models.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html", 
            {
                "request": request, 
                "error": "Incorrect email or password",
                "next": next
            }
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    redirect_url = next if next else "/"
    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response

@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="/static/circlebuy.png", status_code=301)

@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(
    request: Request, 
    product_id: int, 
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_from_cookie)
):
    product = models.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    seller = models.get_user(db, user_id=product.seller_id)
    return templates.TemplateResponse(
        "product_detail.html", 
        {"request": request, "product": product, "seller": seller, "current_user": current_user}
    )

@app.get("/sell", response_class=HTMLResponse)
async def sell_page(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    categories = models.get_categories(db)
    return templates.TemplateResponse("sell.html", {"request": request, "categories": categories, "current_user": current_user})

@app.post("/sell")
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    condition: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        # Validate image
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Limit file size to 5MB
        MAX_SIZE = 5 * 1024 * 1024  # 5MB
        contents = await image.read()
        if len(contents) > MAX_SIZE:
            raise HTTPException(status_code=400, detail="File size too large (max 5MB)")
        
        # Reset file pointer
        await image.seek(0)
        
        # Generate secure filename
        file_extension = os.path.splitext(image.filename)[1].lower()
        allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Invalid file extension")
        
        secure_filename = f"{secrets.token_hex(8)}{file_extension}"
        file_location = f"static/images/products/{secure_filename}"
        
        # Save image
        with open(file_location, "wb") as file_object:
            shutil.copyfileobj(image.file, file_object)
        
        # Create product
        product = models.create_product(
            db=db,
            product=schemas.ProductCreate(
                name=name,
                description=description,
                price=price,
                category_id=category_id,
                condition=condition,
                image_url=f"/static/images/products/{secure_filename}",
                seller_id=current_user.id
            )
        )
        
        return RedirectResponse(url=f"/product/{product.id}", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")

@app.get("/my-products", response_class=HTMLResponse)
async def my_products(
    request: Request,
    sold: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    products = models.get_user_products(db, user_id=current_user.id)
    return templates.TemplateResponse(
        "my_products.html",
        {
            "request": request, 
            "products": products, 
            "current_user": current_user,
            "sold_success": sold == "success"
        }
    )

@app.post("/product/{product_id}/mark-sold")
async def mark_product_sold(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    product = models.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this product")
    
    # Mark as sold
    models.update_product_sold_status(db, product_id=product_id, is_sold=1)
    
    # Schedule immediate cleanup in background (after 1 hour)
    import threading
    def delayed_cleanup():
        time.sleep(3600)  # Wait 1 hour
        try:
            # Remove the sold product and its image
            db_cleanup = SessionLocal()
            sold_product = db_cleanup.query(models.Product).filter(models.Product.id == product_id).first()
            if sold_product and sold_product.is_sold == 1:
                # Delete image
                if sold_product.image_url and sold_product.image_url.startswith("/static/images/products/"):
                    image_path = os.path.join(".", sold_product.image_url.lstrip("/"))
                    if os.path.exists(image_path):
                        os.remove(image_path)
                # Delete product record
                db_cleanup.delete(sold_product)
                db_cleanup.commit()
                print(f"Cleaned up sold product: {sold_product.name}")
            db_cleanup.close()
        except Exception as e:
            print(f"Error in delayed cleanup: {str(e)}")
    
    cleanup_thread = threading.Thread(target=delayed_cleanup, daemon=True)
    cleanup_thread.start()
    
    return RedirectResponse(url="/my-products?sold=success", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    conversations = models.get_user_conversations(db, user_id=current_user.id)
    return templates.TemplateResponse("messages.html", {"request": request, "conversations": conversations, "current_user": current_user})

@app.get("/api/messages/{other_user_id}")
async def get_messages(other_user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    messages = models.get_chat_messages(db, current_user.id, other_user_id)
    return [
        {
            "id": message.id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "content": message.content,
            "timestamp": message.created_at.isoformat(),
            "product_id": message.product_id
        }
        for message in messages
    ]

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Save message to database
            message = models.create_message(
                db=db,
                message=schemas.MessageCreate(
                    sender_id=message_data["sender_id"],
                    receiver_id=message_data["receiver_id"],
                    content=message_data["content"],
                    product_id=message_data.get("product_id")
                )
            )
            
            # Format message for sending
            formatted_message = json.dumps({
                "id": message.id,
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "content": message.content,
                "timestamp": message.created_at.isoformat(),
                "product_id": message.product_id
            })
            
            # Send to both sender and receiver
            await manager.send_personal_message(formatted_message, message.sender_id)
            await manager.send_personal_message(formatted_message, message.receiver_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"Error in websocket: {str(e)}")

@app.get("/search")
async def search(
    request: Request, 
    q: Optional[str] = None, 
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_from_cookie)
):
    if not q:
        # If no query provided, show all products or redirect to home
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    products = models.search_products(db, query=q)
    return templates.TemplateResponse("search_results.html", {"request": request, "products": products, "query": q, "current_user": current_user})

@app.get("/category/{category_id}")
async def category_products(
    request: Request, 
    category_id: int, 
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_from_cookie)
):
    category = models.get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    products = models.get_products_by_category(db, category_id=category_id)
    return templates.TemplateResponse(
        "category.html", 
        {"request": request, "category": category, "products": products, "current_user": current_user}
    )

@app.get("/community")
async def community_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Show community page with users and products from the same domain"""
    if not current_user or not current_user.domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You need to be logged in with a valid email domain to access your community"
        )
    
    # Get domain name (university name)
    domain_name = current_user.university or current_user.domain.split('.')[0].capitalize()
    
    # Get users from the same domain
    users = models.get_users_by_domain(db, domain=current_user.domain)
    
    # Get products from users of the same domain
    products = models.get_products_by_domain(db, domain=current_user.domain)
    
    return templates.TemplateResponse(
        "community.html",
        {
            "request": request,
            "current_user": current_user,
            "domain_name": domain_name,
            "users": users,
            "products": products
        }
    )

def cleanup_task():
    """Background task to clean up old sold products"""
    while True:
        try:
            # Run cleanup every 6 hours for better storage management
            time.sleep(21600)  # 6 hours in seconds
            count = cleanup_sold_products(days_to_keep=7)  # Keep sold items for only 7 days
            print(f"Cleaned up {count} old sold products")
            
            # Also cleanup orphaned images
            from cleanup import cleanup_orphaned_images
            orphaned = cleanup_orphaned_images()
            if orphaned > 0:
                print(f"Removed {orphaned} orphaned images")
        except Exception as e:
            print(f"Error in cleanup task: {str(e)}")

@app.get("/admin/storage")
async def storage_stats(request: Request, db: Session = Depends(get_db)):
    """Storage management page - shows storage stats and cleanup options"""
    from cleanup import get_storage_stats
    stats = get_storage_stats()
    
    return templates.TemplateResponse("storage_admin.html", {
        "request": request,
        "stats": stats
    })

@app.post("/admin/cleanup")
async def manual_cleanup(db: Session = Depends(get_db)):
    """Manual cleanup trigger"""
    try:
        # Cleanup sold products
        cleaned = cleanup_sold_products(days_to_keep=7)
        
        # Cleanup orphaned images
        orphaned = cleanup_orphaned_images()
        
        return {"success": True, "cleaned_products": cleaned, "orphaned_images": orphaned}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Start cleanup task in background
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=8000)