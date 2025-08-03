from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.models.user import User, Role, Permission, user_roles, role_permissions
from app.models.stock import UserWatchlist, StockInfo
from app.core.config import settings
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from loguru import logger

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    """用户服务类"""
    
    def __init__(self):
        self.pwd_context = pwd_context
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """生成密码哈希"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).options(
            joinedload(User.roles).joinedload(Role.permissions)
        ).filter(User.username == username).first()
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).options(
            joinedload(User.roles).joinedload(Role.permissions)
        ).filter(User.id == user_id).first()
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = self.get_user_by_username(db, username)
        if not user:
            user = self.get_user_by_email(db, username)
        
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        return user
    
    def create_user(self, db: Session, user_create: UserCreate) -> User:
        """创建用户"""
        try:
            # 检查用户名是否已存在
            if self.get_user_by_username(db, user_create.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已存在"
                )
            
            # 检查邮箱是否已存在
            if self.get_user_by_email(db, user_create.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已存在"
                )
            
            # 创建用户
            hashed_password = self.get_password_hash(user_create.password)
            user = User(
                username=user_create.username,
                email=user_create.email,
                full_name=user_create.full_name,
                hashed_password=hashed_password,
                is_active=True
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # 分配默认角色（普通用户）
            default_role = db.query(Role).filter(Role.name == "user").first()
            if default_role:
                user_role = UserRole(user_id=user.id, role_id=default_role.id)
                db.add(user_role)
                db.commit()
            
            logger.info(f"用户创建成功: {user.username}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建用户失败"
            )
    
    def update_user(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        try:
            user = self.get_user_by_id(db, user_id)
            if not user:
                return None
            
            # 更新字段
            update_data = user_update.dict(exclude_unset=True)
            
            # 检查邮箱唯一性
            if "email" in update_data:
                existing_user = self.get_user_by_email(db, update_data["email"])
                if existing_user and existing_user.id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="邮箱已存在"
                    )
            
            # 处理密码更新
            if "password" in update_data:
                update_data["hashed_password"] = self.get_password_hash(update_data.pop("password"))
            
            # 更新用户信息
            for field, value in update_data.items():
                setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            
            logger.info(f"用户信息更新成功: {user.username}")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"更新用户失败: {e}")
            db.rollback()
            return None
    
    def change_password(self, db: Session, user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        try:
            user = self.get_user_by_id(db, user_id)
            if not user:
                return False
            
            # 验证旧密码
            if not self.verify_password(old_password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="原密码错误"
                )
            
            # 更新密码
            user.hashed_password = self.get_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"用户密码修改成功: {user.username}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            db.rollback()
            return False
    
    def delete_user(self, db: Session, user_id: int) -> bool:
        """删除用户（软删除）"""
        try:
            user = self.get_user_by_id(db, user_id)
            if not user:
                return False
            
            # 软删除
            user.is_active = False
            user.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"用户删除成功: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            db.rollback()
            return False
    
    def get_users(self, db: Session, skip: int = 0, limit: int = 100, 
                  search: Optional[str] = None, is_active: Optional[bool] = None) -> List[User]:
        """获取用户列表"""
        try:
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
            
            return query.offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return []
    
    def get_user_roles(self, db: Session, user_id: int) -> List[Role]:
        """获取用户角色"""
        try:
            roles = db.query(Role).join(
                UserRole, Role.id == UserRole.role_id
            ).filter(
                UserRole.user_id == user_id
            ).all()
            
            return roles
            
        except Exception as e:
            logger.error(f"获取用户角色失败: {e}")
            return []
    
    def get_user_permissions(self, db: Session, user_id: int) -> List[Permission]:
        """获取用户权限"""
        try:
            permissions = db.query(Permission).join(
                RolePermission, Permission.id == RolePermission.permission_id
            ).join(
                UserRole, RolePermission.role_id == UserRole.role_id
            ).filter(
                UserRole.user_id == user_id
            ).distinct().all()
            
            return permissions
            
        except Exception as e:
            logger.error(f"获取用户权限失败: {e}")
            return []
    
    def has_permission(self, db: Session, user_id: int, permission_name: str) -> bool:
        """检查用户是否有指定权限"""
        try:
            permission = db.query(Permission).join(
                RolePermission, Permission.id == RolePermission.permission_id
            ).join(
                UserRole, RolePermission.role_id == UserRole.role_id
            ).filter(
                and_(
                    UserRole.user_id == user_id,
                    Permission.name == permission_name
                )
            ).first()
            
            return permission is not None
            
        except Exception as e:
            logger.error(f"检查用户权限失败: {e}")
            return False
    
    def has_role(self, db: Session, user_id: int, role_name: str) -> bool:
        """检查用户是否有指定角色"""
        try:
            role = db.query(Role).join(
                UserRole, Role.id == UserRole.role_id
            ).filter(
                and_(
                    UserRole.user_id == user_id,
                    Role.name == role_name
                )
            ).first()
            
            return role is not None
            
        except Exception as e:
            logger.error(f"检查用户角色失败: {e}")
            return False
    
    def assign_role(self, db: Session, user_id: int, role_id: int) -> bool:
        """分配角色给用户"""
        try:
            # 检查是否已存在
            existing = db.query(UserRole).filter(
                and_(
                    UserRole.user_id == user_id,
                    UserRole.role_id == role_id
                )
            ).first()
            
            if existing:
                return True
            
            # 创建新的角色分配
            user_role = UserRole(user_id=user_id, role_id=role_id)
            db.add(user_role)
            db.commit()
            
            logger.info(f"角色分配成功: user_id={user_id}, role_id={role_id}")
            return True
            
        except Exception as e:
            logger.error(f"分配角色失败: {e}")
            db.rollback()
            return False
    
    def remove_role(self, db: Session, user_id: int, role_id: int) -> bool:
        """移除用户角色"""
        try:
            user_role = db.query(UserRole).filter(
                and_(
                    UserRole.user_id == user_id,
                    UserRole.role_id == role_id
                )
            ).first()
            
            if user_role:
                db.delete(user_role)
                db.commit()
                logger.info(f"角色移除成功: user_id={user_id}, role_id={role_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"移除角色失败: {e}")
            db.rollback()
            return False
    
    def get_user_watchlist(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """获取用户自选股"""
        try:
            watchlist = db.query(
                UserWatchlist,
                StockInfo.name.label('stock_name'),
                StockInfo.market
            ).join(
                StockInfo, UserWatchlist.stock_code == StockInfo.code
            ).filter(
                UserWatchlist.user_id == user_id
            ).order_by(
                UserWatchlist.sort_order,
                UserWatchlist.created_at
            ).all()
            
            result = []
            for item in watchlist:
                watchlist_item, stock_name, market = item
                result.append({
                    "id": watchlist_item.id,
                    "stock_code": watchlist_item.stock_code,
                    "stock_name": stock_name,
                    "market": market,
                    "sort_order": watchlist_item.sort_order,
                    "notes": watchlist_item.notes,
                    "created_at": watchlist_item.created_at
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取用户自选股失败: {e}")
            return []
    
    def add_to_watchlist(self, db: Session, user_id: int, stock_code: str, notes: Optional[str] = None) -> bool:
        """添加股票到自选股"""
        try:
            # 检查是否已存在
            existing = db.query(UserWatchlist).filter(
                and_(
                    UserWatchlist.user_id == user_id,
                    UserWatchlist.stock_code == stock_code
                )
            ).first()
            
            if existing:
                return True
            
            # 获取下一个排序号
            max_order = db.query(func.max(UserWatchlist.sort_order)).filter(
                UserWatchlist.user_id == user_id
            ).scalar() or 0
            
            # 添加到自选股
            watchlist_item = UserWatchlist(
                user_id=user_id,
                stock_code=stock_code,
                sort_order=max_order + 1,
                notes=notes
            )
            
            db.add(watchlist_item)
            db.commit()
            
            logger.info(f"添加自选股成功: user_id={user_id}, stock_code={stock_code}")
            return True
            
        except Exception as e:
            logger.error(f"添加自选股失败: {e}")
            db.rollback()
            return False
    
    def remove_from_watchlist(self, db: Session, user_id: int, stock_code: str) -> bool:
        """从自选股中移除股票"""
        try:
            watchlist_item = db.query(UserWatchlist).filter(
                and_(
                    UserWatchlist.user_id == user_id,
                    UserWatchlist.stock_code == stock_code
                )
            ).first()
            
            if watchlist_item:
                db.delete(watchlist_item)
                db.commit()
                logger.info(f"移除自选股成功: user_id={user_id}, stock_code={stock_code}")
            
            return True
            
        except Exception as e:
            logger.error(f"移除自选股失败: {e}")
            db.rollback()
            return False
    
    def get_user_stats(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取用户统计信息"""
        try:
            # 自选股数量
            watchlist_count = db.query(func.count(UserWatchlist.id)).filter(
                UserWatchlist.user_id == user_id
            ).scalar() or 0
            
            # 用户信息
            user = self.get_user_by_id(db, user_id)
            if not user:
                return {}
            
            return {
                "user_id": user_id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "last_login_at": user.last_login_at,
                "watchlist_count": watchlist_count,
                "roles": [role.name for role in self.get_user_roles(db, user_id)]
            }
            
        except Exception as e:
            logger.error(f"获取用户统计信息失败: {e}")
            return {}

# 创建全局服务实例
user_service = UserService()