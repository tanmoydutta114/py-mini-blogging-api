
from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app.models import User


class UserSchema(SQLAlchemyAutoSchema):
    
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)
        dump_only = ('id', 'created_at', 'updated_at')
    
    full_name = fields.Method("get_full_name")
    
    def get_full_name(self, obj: User) -> str:
        return obj.full_name


class UserRegistrationSchema(Schema):
    
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=80),
            validate.Regexp(
                r'^[a-zA-Z0-9_]+$',
                error="Username can only contain letters, numbers, and underscores"
            )
        ]
    )
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=128),
            validate.Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
                error="Password must contain at least one lowercase letter, one uppercase letter, and one digit"
            )
        ]
    )
    confirm_password = fields.Str(required=True)
    first_name = fields.Str(validate=validate.Length(max=50), allow_none=True)
    last_name = fields.Str(validate=validate.Length(max=50), allow_none=True)
    
    @validates('username')
    def validate_username(self, value: str) -> None:
        if User.query.filter_by(username=value).first():
            raise ValidationError("Username already exists")
    
    @validates('email')
    def validate_email(self, value: str) -> None:
        if User.query.filter_by(email=value).first():
            raise ValidationError("Email already registered")
    
    def validate(self, data, **kwargs):
        errors = {}
        
        if data.get('password') != data.get('confirm_password'):
            errors['confirm_password'] = ['Passwords do not match']
        
        if errors:
            raise ValidationError(errors)
        
        return data


class UserLoginSchema(Schema):
    
    username = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=1, max=128))


class UserUpdateSchema(Schema):
    
    first_name = fields.Str(validate=validate.Length(max=50), allow_none=True)
    last_name = fields.Str(validate=validate.Length(max=50), allow_none=True)
    email = fields.Email(validate=validate.Length(max=120))
    