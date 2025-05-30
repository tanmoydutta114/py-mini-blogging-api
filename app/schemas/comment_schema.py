from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app.models import Comment, Post


class CommentSchema(SQLAlchemyAutoSchema):
    
    class Meta:
        model = Comment
        load_instance = True
    author_id = fields.Int(dump_only=True)



class CommentCreateSchema(Schema):
    
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'Name is required'}
    )
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={'required': 'Content is required'}
    )
    post_id = fields.Int(
        required=True,
        error_messages={'required': 'Post ID is required'}
    )
    
    @validates('name')
    def validate_name(self, value: str) -> None:
        if not value.strip():
            raise ValidationError("Name cannot be empty or just whitespace")
    
    @validates('content')
    def validate_content(self, value: str) -> None:
        if not value.strip():
            raise ValidationError("Content cannot be empty or just whitespace")
    
    @validates('post_id')
    def validate_post_exists(self, value: int) -> None:
        if not Post.query.get(value):
            raise ValidationError("Post not found")


class CommentUpdateSchema(Schema):
    
    name = fields.Str(validate=validate.Length(min=1, max=100))
    content = fields.Str(validate=validate.Length(min=1))
    
    @validates('name')
    def validate_name(self, value: str) -> None:
        if value is not None and not value.strip():
            raise ValidationError("Name cannot be empty or just whitespace")
    
    @validates('content')
    def validate_content(self, value: str) -> None:
        if value is not None and not value.strip():
            raise ValidationError("Content cannot be empty or just whitespace")