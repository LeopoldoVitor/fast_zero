from fastapi import APIRouter
from fastapi import HTTPException, Depends

from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session
from models import User
from security import get_password_hash, get_current_user
from schemas import Message, UserSchema, UserPublic, UserList
from http import HTTPStatus
from typing import Annotated

router = APIRouter(prefix='/users', tags=['users'])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: T_Session):
    user_alredy_exists(user, session)

    user_db = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db


@router.get('/', response_model=UserList)
def read_users(session: T_Session):
    users = session.scalars(select(User))
    return {'users': users}


@router.get('/{user_id}', response_model=UserPublic)
def read_one_user(user_id: int, session: T_Session):
    user_not_found(user_id, session)
    db_user = session.scalar(select(User).where(User.id == user_id))
    return db_user


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    check_permissions(current_user, user_id)
    user_alredy_exists(user, session)

    current_user.email = user.email
    current_user.username = user.username
    current_user.password = get_password_hash(user.password)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    check_permissions(current_user, user_id)

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}


def user_not_found(user_id: int, session):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )


def user_alredy_exists(user: UserSchema, session):
    user_db = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if user_db:
        if user_db.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username alredy exists',
            )
        if user_db.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email alredy exists',
            )


def check_permissions(current_user, user_id):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )
