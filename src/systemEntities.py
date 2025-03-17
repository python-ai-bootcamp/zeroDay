from pydantic import BaseModel

class User(BaseModel):
    email: str
    hacker_id: str
    name: str
    phone: str
