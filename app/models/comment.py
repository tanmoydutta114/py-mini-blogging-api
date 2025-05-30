
from datetime import datetime
from typing import TYPE_CHECKING

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .user import User
    from .post import Post

from app.extensions import db


class Comment(db.Model):
    
    __tablename__ = 'comments'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('posts.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    author_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    def __init__(self, name: str, content: str, post_id: int, author_id: int) -> None:
        self.name = name
        self.content = content
        self.post_id = post_id
        self.author_id = author_id
    
    @property
    def excerpt(self) -> str:
        if len(self.content) <= 100:
            return self.content
        return self.content[:97] + "..."
    
    def to_dict(self, include_author: bool = True, include_post: bool = False) -> dict:
        data = {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_author and self.author:
            data['author'] = self.author.to_dict()
            
        if include_post and self.post:
            data['post'] = {
                'id': self.post.id,
                'title': self.post.title,
                'slug': self.post.slug
            }
            
        return data
    
    def can_edit(self, user_id: int) -> bool:
        return self.author_id == user_id
    
    def can_delete(self, user_id: int) -> bool:
        return self.author_id == user_id
    
    def __repr__(self) -> str:
        return f'<Comment by {self.name} on "{self.post.title if self.post else "Unknown"}">'