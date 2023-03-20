import pydantic
from typing import Optional


class RegisterUser(pydantic.BaseModel):
    email: pydantic.EmailStr
    password: str

    @pydantic.validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("password is too short")
        return value


class LoginUser(pydantic.BaseModel):
    email: pydantic.EmailStr
    password: str


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
