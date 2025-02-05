from pydantic import BaseModel, ConfigDict


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: str
    password: str


class UserDB(UserSchema):
    id: int


class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str
