from fastapi import FastAPI, HTTPException, Depends
from http import HTTPStatus
from schemas import Message, UserSchema, UserPublic, UserList, Token
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_session
from models import User
from security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Ola, Mundo'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
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


@app.get('/users/', response_model=UserList)
def read_users(
    session: Session = Depends(get_session),
):
    users = session.scalars(select(User))
    return {'users': users}


@app.get('/users/{user_id}', response_model=UserPublic)
def read_one_user(user_id: int, session: Session = Depends(get_session)):
    user_not_found(user_id, session)
    db_user = session.scalar(select(User).where(User.id == user_id))
    return db_user


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=400,
            detail='Not enough permissions',
        )
    user_alredy_exists(user, session)

    current_user.email = user.email
    current_user.username = user.username
    current_user.password = get_password_hash(user.password)
    session.commit()
    session.refresh(current_user)

    return current_user


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=400,
            detail='Not enough permissions',
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}


@app.post('/token', response_model=Token)
def login_for_acess_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400, detail='Incorrect email or password'
        )
    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}


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
