from fastapi import APIRouter, Depends, HTTPException
from models import User, Todo, TodoState
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from security import get_current_user, get_session
from schemas import TodoSchema, TodoPublic, TodoList, Message
from http import HTTPStatus


router = APIRouter(prefix='/todos', tags=['todo'])

CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[Session, Depends(get_session)]


@router.post('/', response_model=TodoPublic)
def create_todo(
    todo: TodoSchema,
    user: CurrentUser,
    session: T_Session,
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
def read_todos(  # noqa
    user: CurrentUser,
    session: T_Session,
    title: str | None = None,
    description: str | None = None,
    state: TodoState | None = None,
    offset: int | None = None,
    limit: int | None = None,
):
    query = select(Todo).where(Todo.user_id == user.id)

    if title:
        query = query.filter(Todo.title.contains(title))
    if description:
        query = query.filter(Todo.description.contains(description))
    if state:
        query = query.filter(Todo.state == state)

    todos = session.scalars(query.offset(offset).limit(limit)).all()

    return {'todos': todos}


@router.delete('/{todo_id}', response_model=Message)
def delete_todo(todo_id: int, user: CurrentUser, session: T_Session):
    task = session.scalar(select(Todo).where(Todo.id == todo_id))
    if not task:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found'
        )

    session.delete(task)
    session.commit()

    return {'message': 'Task deleted'}
