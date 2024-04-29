from pydantic import BaseModel, EmailStr


class NewsLetterObject(BaseModel):
    name: str
    email: EmailStr
    affiliation: str
