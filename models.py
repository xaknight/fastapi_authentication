from pydantic import BaseModel

class User(BaseModel):
    id: str
    email: str
    name: str
    picture: str | None = None
    # ... other fields ...