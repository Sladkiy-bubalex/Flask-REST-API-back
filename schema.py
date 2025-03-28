from pydantic import BaseModel, field_validator, ValidationError
from typing import Tuple
from errors import HttpError


class CreateAdSchema(BaseModel):
    title: str
    description: str


class UpdateAdSchema(BaseModel):
    title: str | None = None
    description: str | None = None


class BaseUserSchema(BaseModel):
    email: str
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, password):
        if password is not None and len(password) < 8:
            raise ValueError('password less than 8 characters')
        return password


class CreateUserSchema(BaseUserSchema):
    pass


class UpdateUserSchema(BaseUserSchema):
    email: str | None = None
    password: str | None = None


SchemasTypes = Tuple[
    type[CreateAdSchema],
    type[UpdateAdSchema],
    type[CreateUserSchema],
    type[UpdateUserSchema]
]


def validate_json(schema_cls: SchemasTypes, json_data: dict):
    try:
        check_validate = schema_cls(**json_data)
        return check_validate.dict(exclude_unset=True)
    except ValidationError as e:
        errors = e.errors()
        for error in errors:
            error.pop('ctx', None)
        raise HttpError(400, errors)
