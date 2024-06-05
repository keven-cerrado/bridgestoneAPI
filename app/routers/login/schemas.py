from pydantic import BaseModel


class User(BaseModel):
    username: str
    disabled: bool | None = None
    
class UserInDB(User):
    hashed_password: str