"""Authentication and User Pydantic schemas."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UserBase(BaseModel):
    email: EmailStr = Field(description="User primary email address")
    full_name: str = Field(min_length=1, max_length=255, description="Full name of user")


# A short list of passwords that pass the length rule but are still guessed first.
_COMMON_LONG_PASSWORDS = {
    "password1234", "123456789012", "qwertyuiop12", "passwordpassword", "iloveyou1234",
    "letmein12345", "welcome12345", "administrator", "1234567890123", "qwerty123456",
}


class UserCreate(UserBase):
    password: str = Field(
        min_length=12,
        max_length=128,
        description="Plaintext password: 12 to 128 characters",
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(set(v)) < 4:
            raise ValueError("Password is too repetitive. Use a mix of at least 4 different characters.")
        if v.lower() in _COMMON_LONG_PASSWORDS:
            raise ValueError("This password is too common. Choose a different one.")
        return v

    @model_validator(mode="after")
    def password_not_email(self) -> "UserCreate":
        local_part = self.email.split("@")[0].lower()
        if len(local_part) >= 4 and local_part in self.password.lower():
            raise ValueError("Password must not contain your email address.")
        return self


class AccountDeleteRequest(BaseModel):
    password: str = Field(min_length=1, description="Current password, to confirm deletion")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
