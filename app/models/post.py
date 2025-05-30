
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .user import User
    from .comment import Comment

from app.extensions import db


class Post(db.Model):
    
    __tablename__ = 'posts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    slug: Mapped[Optional[str]] = mapped_column(String(200), unique=True, index=True)
    is_published: Mapped[bool] = mapped_column(default=True, nullable=False)
    
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
    

    def __init__(self, title: str, content: str, author_id: int, 
                 slug: Optional[str] = None, is_published: bool = True) -> None:
        self.title = title
        self.content = content
        self.author_id = author_id
        self.slug = slug or self._generate_slug(title)
        self.is_published = is_published
    
    def _generate_slug(self, title: str) -> str:
        import re
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')[:200]  # Limit to 200 characters
    
    @property
    def excerpt(self) -> str:
        if len(self.content) <= 200:
            return self.content
        return self.content[:197] + "..."
    
    @property
    def comment_count(self) -> int:
        return self.comments.count()
    
    def to_dict(self, include_content: bool = True, include_author: bool = True) -> dict:
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'comment_count': self.comment_count
        }
        
        if include_content:
            data['content'] = self.content
        else:
            data['excerpt'] = self.excerpt
            
        if include_author and self.author:
            data['author'] = self.author.to_dict()
            
        return data
    
    def can_edit(self, user_id: int) -> bool:
        return self.author_id == user_id
    
    def can_delete(self, user_id: int) -> bool:
        return self.author_id == user_id
    
    def __repr__(self) -> str:
        return f'<Post "{self.title}" by {self.author.username if self.author else "Unknown"}>'