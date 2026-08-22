"""用户管理 API 路由

定义 CRUD 端点，通过 Depends(get_db) 注入数据库会话。
使用 APIRouter 便于模块化组织路由。
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建一个新用户。username 和 email 必须唯一。",
)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)) -> schemas.UserResponse:
    """创建用户端点

    业务校验：username 和 email 不能与已有用户重复。
    """
    # 唯一性校验：避免在数据库层面抛出 IntegrityError
    if crud.get_user_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已被占用",
        )
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="邮箱已被注册",
        )

    user = crud.create_user(db, user_in)
    return user


@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse,
    summary="获取单个用户",
)
def get_user(user_id: int, db: Session = Depends(get_db)) -> schemas.UserResponse:
    """根据 ID 获取用户"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 ID {user_id} 不存在",
        )
    return user


@router.get(
    "/",
    response_model=list[schemas.UserResponse],
    summary="获取用户列表",
    description="支持分页查询，使用 skip 和 limit 参数。",
)
def list_users(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数（1-100）"),
    db: Session = Depends(get_db),
) -> list[schemas.UserResponse]:
    """分页获取用户列表"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.put(
    "/{user_id}",
    response_model=schemas.UserResponse,
    summary="更新用户",
)
def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
) -> schemas.UserResponse:
    """更新用户信息（支持部分更新）

    若传入 username/email，会进行唯一性校验。
    """
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 ID {user_id} 不存在",
        )

    # 仅在用户实际传入这些字段时才做唯一性校验
    update_data = user_in.model_dump(exclude_unset=True)
    if "username" in update_data and update_data["username"] != db_user.username:
        existing = crud.get_user_by_username(db, update_data["username"])
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="用户名已被占用",
            )
    if "email" in update_data and update_data["email"] != db_user.email:
        existing = crud.get_user_by_email(db, update_data["email"])
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="邮箱已被注册",
            )

    user = crud.update_user(db, db_user, update_data)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除用户",
)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    """删除用户"""
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 ID {user_id} 不存在",
        )
    crud.delete_user(db, db_user)
