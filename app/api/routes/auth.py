from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import timedelta

from app.core.database import get_session
from app.models.sql_schemas import User
from app.core.security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.api.deps import require_role
from pydantic import BaseModel
from typing import List

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: str
    password: str

class UserInfo(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool

class RoleUpdate(BaseModel):
    role: str  # "user" or "admin"

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_session)):
    # Check if user exists
    stmt = select(User).where(User.email == user_in.email)
    result = await db.exec(stmt)
    existing_user = result.first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    new_user = User(
        email=user_in.email, 
        hashed_password=get_password_hash(user_in.password),
        role="user"
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email, "role": new_user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    # Find user
    stmt = select(User).where(User.email == form_data.username)
    result = await db.exec(stmt)
    user = result.first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Admin-only User Management ---

@router.get("/users", response_model=List[UserInfo])
async def list_users(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
):
    """List all users (admin only)."""
    stmt = select(User)
    result = await db.exec(stmt)
    users = result.all()
    return [
        UserInfo(id=u.id, email=u.email, role=u.role, is_active=u.is_active)
        for u in users
    ]

@router.patch("/users/{user_id}/role", response_model=UserInfo)
async def update_user_role(
    user_id: int,
    role_update: RoleUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
):
    """Change a user's role (admin only). Valid roles: 'user', 'admin'."""
    if role_update.role not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Role must be 'user' or 'admin'")
    
    stmt = select(User).where(User.id == user_id)
    result = await db.exec(stmt)
    user = result.first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = role_update.role
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserInfo(id=user.id, email=user.email, role=user.role, is_active=user.is_active)
