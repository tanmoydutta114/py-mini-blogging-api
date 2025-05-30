"""Configuration settings for the Flask application."""

import os
from datetime import timedelta
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""
    
    # Basic Flask configuration
    SECRET_KEY: str = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI: str = os.environ.get('DATABASE_URL') or 'sqlite:///blog.db'
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ECHO: bool = False
    
    # JWT configuration
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=30)
    
    # Pagination
    POSTS_PER_PAGE: int = 10
    COMMENTS_PER_PAGE: int = 20
    
    # Security
    BCRYPT_LOG_ROUNDS: int = 12
    
    # CORS
    CORS_ORIGINS: list[str] = ['http://localhost:3000', 'http://127.0.0.1:3000']


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG: bool = True
    SQLALCHEMY_ECHO: bool = True
    BCRYPT_LOG_ROUNDS: int = 4  # Faster for development


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG: bool = False
    SQLALCHEMY_ECHO: bool = False
    
    # Override with environment variables in production
    SECRET_KEY: str = os.environ.get('SECRET_KEY') or ''
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY') or ''
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production")
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY must be set in production")


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///:memory:'
    BCRYPT_LOG_ROUNDS: int = 4
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(seconds=1)


# Configuration dictionary
config: dict[str, type[Config]] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}