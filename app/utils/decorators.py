
from functools import wraps
from typing import Callable, Any

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.models import User


def validate_json(schema_class: type) -> Callable:
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                if not request.is_json:
                    return jsonify({'error': 'Request must be JSON'}), 400
                
                json_data = request.get_json()
                if not json_data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                schema = schema_class()
                print(f"Validating JSON data: {json_data}")
                validated_data = schema.load(json_data)
                print(f"Validated data: {validated_data}")
                
                kwargs['validated_data'] = validated_data
                
                return func(*args, **kwargs)
                
            except ValidationError as err:
                return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
            except Exception as err:
                print(err)
                return jsonify({'error': 'Invalid JSON data'}), 400
        
        return wrapper
    return decorator


def auth_required(func: Callable) -> Callable:
    
    @wraps(func)
    @jwt_required()
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            current_user_id = get_jwt_identity()
            
            current_user = User.query.get(current_user_id)
            if not current_user or not current_user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            kwargs['current_user'] = current_user
            
            return func(*args, **kwargs)
            
        except Exception as err:
            return jsonify({'error': 'Authentication failed'}), 401
    
    return wrapper


def handle_db_errors(func: Callable) -> Callable:
    
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as err:
            print(f"Database error in {func.__name__}: {str(err)}")
            return jsonify({'error': 'Database operation failed'}), 500
    
    return wrapper


def paginate_query(default_per_page: int = 10, max_per_page: int = 100) -> Callable:
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', default_per_page, type=int)
            
            if page < 1:
                return jsonify({'error': 'Page must be >= 1'}), 400
            
            if per_page < 1 or per_page > max_per_page:
                return jsonify({'error': f'Per page must be between 1 and {max_per_page}'}), 400
            
            kwargs['page'] = page
            kwargs['per_page'] = per_page
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def cors_headers(func: Callable) -> Callable:
    
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        response = func(*args, **kwargs)
        
        if isinstance(response, tuple):
            response_data, status_code = response
            if hasattr(response_data, 'headers'):
                response_data.headers['Access-Control-Allow-Origin'] = '*'
                response_data.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response_data.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
    
    return wrapper