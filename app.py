from fastapi import FastAPI

from schemas import Message
from http import HTTPStatus
from routers import users, auth, todo

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todo.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Ola, Mundo'}
