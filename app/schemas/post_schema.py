
from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app.models import Post


class PostSchema(SQLAlchemyAutoSchema):
    
    class Meta:
        model = Post
        load_instance = True



class PostCreateSchema(Schema):
   
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={'required': 'Title is required'}
    )
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={'required': 'Content is required'}
    )
    is_published = fields.Bool(missing=True)
    
    @validates('title')
    def validate_title(self, value: str) -> None:
       
        if not value.strip():
            raise ValidationError("Title cannot be empty or just whitespace")
    
    @validates('content')
    def validate_content(self, value: str) -> None:

        if not value.strip():
            raise ValidationError("Content cannot be empty or just whitespace")


class PostUpdateSchema(Schema):

    
    title = fields.Str(validate=validate.Length(min=1, max=200))
    content = fields.Str(validate=validate.Length(min=1))
    is_published = fields.Bool()
    
    @validates('title')
    def validate_title(self, value: str) -> None:

        if value is not None and not value.strip():
            raise ValidationError("Title cannot be empty or just whitespace")
    
    @validates('content')
    def validate_content(self, value: str) -> None:

        if value is not None and not value.strip():
            raise ValidationError("Content cannot be empty or just whitespace")


class PostListSchema(PostSchema):
    
    class Meta(PostSchema.Meta):
        exclude = ('content',)