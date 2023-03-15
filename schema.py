import pydantic
from typing import Optional


class User(pydantic.BaseModel):
    email: pydantic.EmailStr
    password: str

    @pydantic.validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("password is too short")
        return value


class CreateUser(User):
    """CreateUser"""


class PatchUser(User):
    """PatchUser"""

    email: Optional[pydantic.EmailStr]
    password: Optional[str]


class CreateAdvertisement(pydantic.BaseModel):
    """CreateAdvertisement"""

    title: str
    description: str
    user_id: int


class PatchAdvertisement(pydantic.BaseModel):
    """PatchAdvertisement"""

    title: Optional[str]
    description: Optional[str]
    user_id: int
