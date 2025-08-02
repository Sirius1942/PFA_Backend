from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.models.user import User, Role
from app.auth.jwt import JWTManager
from app.core.deps import get_current_user
from app.auth.permissions import require_permission
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter(tags=["用户管理"])
jwt_manager = JWTManager()

# Pydantic模型
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: List[str] = []
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role_names: List[str] = ["user"]

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role_names: Optional[List[str]] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    user_data = UserResponse.from_orm(current_user)
    user_data.roles = [role.name for role in current_user.roles]
    return user_data

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    # 用户只能更新自己的基本信息，不能更改角色
    if user_update.username:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(
            and_(User.username == user_update.username, User.id != current_user.id)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        current_user.username = user_update.username
    
    if user_update.email:
        # 检查邮箱是否已存在
        existing_user = db.query(User).filter(
            and_(User.email == user_update.email, User.id != current_user.id)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        current_user.email = user_update.email
    
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    user_data = UserResponse.from_orm(current_user)
    user_data.roles = [role.name for role in current_user.roles]
    return user_data

@router.post("/me/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改当前用户密码"""
    from app.auth.jwt import PasswordManager
    password_manager = PasswordManager()
    
    # 验证旧密码
    if not password_manager.verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    # 设置新密码
    current_user.hashed_password = password_manager.hash_password(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "密码修改成功"}

@router.get("/", response_model=List[UserResponse])
@require_permission("manage_users")
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    role_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户列表（管理员权限）"""
    query = db.query(User)
    
    # 搜索过滤
    if search:
        query = query.filter(
            or_(
                User.username.contains(search),
                User.email.contains(search),
                User.full_name.contains(search)
            )
        )
    
    # 状态过滤
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # 角色过滤
    if role_name:
        query = query.join(User.roles).filter(Role.name == role_name)
    
    users = query.offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        user_data = UserResponse.from_orm(user)
        user_data.roles = [role.name for role in user.roles]
        result.append(user_data)
    
    return result

@router.post("/", response_model=UserResponse)
@require_permission("manage_users")
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新用户（管理员权限）"""
    from app.auth.jwt import PasswordManager
    password_manager = PasswordManager()
    
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 创建用户
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=password_manager.hash_password(user_data.password),
        is_active=True
    )
    
    # 分配角色
    roles = db.query(Role).filter(Role.name.in_(user_data.role_names)).all()
    if not roles:
        # 如果没有找到指定角色，分配默认用户角色
        default_role = db.query(Role).filter(Role.name == "user").first()
        if default_role:
            roles = [default_role]
    
    new_user.roles = roles
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    user_response = UserResponse.from_orm(new_user)
    user_response.roles = [role.name for role in new_user.roles]
    return user_response

@router.get("/{user_id}", response_model=UserResponse)
@require_permission("manage_users")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定用户信息（管理员权限）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user_data = UserResponse.from_orm(user)
    user_data.roles = [role.name for role in user.roles]
    return user_data

@router.put("/{user_id}", response_model=UserResponse)
@require_permission("manage_users")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新指定用户信息（管理员权限）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新基本信息
    if user_update.username:
        existing_user = db.query(User).filter(
            and_(User.username == user_update.username, User.id != user_id)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        user.username = user_update.username
    
    if user_update.email:
        existing_user = db.query(User).filter(
            and_(User.email == user_update.email, User.id != user_id)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        user.email = user_update.email
    
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    # 更新角色
    if user_update.role_names is not None:
        roles = db.query(Role).filter(Role.name.in_(user_update.role_names)).all()
        user.roles = roles
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    user_data = UserResponse.from_orm(user)
    user_data.roles = [role.name for role in user.roles]
    return user_data

@router.delete("/{user_id}")
@require_permission("manage_users")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除指定用户（管理员权限）"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "用户删除成功"}

@router.get("/roles/available")
@require_permission("manage_users")
async def get_available_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取可用角色列表（管理员权限）"""
    roles = db.query(Role).all()
    return [
        {
            "name": role.name,
            "description": role.description,
            "permissions": [perm.name for perm in role.permissions]
        }
        for role in roles
    ]