
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from app import db
from app.models import User
from app.schemas import UserRegistrationSchema, UserLoginSchema, UserSchema
from app.utils.decorators import validate_json, auth_required


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
@validate_json(UserRegistrationSchema)
def register(validated_data: dict) -> tuple:
    try:
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name')
        )

        if validated_data['password'] != validated_data['confirm_password']:
            return jsonify({'error':'Password and confirm password should be same!'}), 401
        
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        user_schema = UserSchema()
        user_data = user_schema.dump(user)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user_data,
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as err:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(err)}), 500


@auth_bp.route('/login', methods=['POST'])
@validate_json(UserLoginSchema)
def login(validated_data: dict) -> tuple:
    try:
        user = User.query.filter_by(username=validated_data['username']).first()
        
        if not user or not user.check_password(validated_data['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        user_schema = UserSchema()
        user_data = user_schema.dump(user)
        
        return jsonify({
            'message': 'Login successful',
            'user': user_data,
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as err:
        return jsonify({'error': 'Login failed', 'details': str(err)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh() -> tuple:
    try:
        current_user_id = get_jwt_identity()
        
        user = User.query.get(current_user_id)
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as err:
        return jsonify({'error': 'Token refresh failed', 'details': str(err)}), 500


@auth_bp.route('/me', methods=['GET'])
@auth_required
def get_current_user(current_user: User) -> tuple:
    try:
        user_schema = UserSchema()
        user_data = user_schema.dump(current_user)
        
        return jsonify({
            'user': user_data
        }), 200
        
    except Exception as err:
        return jsonify({'error': 'Failed to get user profile', 'details': str(err)}), 500



@auth_bp.route('/me', methods=['PUT'])
@auth_required
def update_profile(current_user: User) -> tuple:
    """Update current user profile."""
    try:
        # Get JSON data
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Update allowed fields
        if 'first_name' in json_data:
            current_user.first_name = json_data['first_name']
        if 'last_name' in json_data:
            current_user.last_name = json_data['last_name']
        if 'email' in json_data:
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=json_data['email']).first()
            if existing_user and existing_user.id != current_user.id:
                return jsonify({'error': 'Email already taken'}), 400
            current_user.email = json_data['email']
        
        # Save changes
        db.session.commit()
        
        # Return updated user data
        user_schema = UserSchema()
        user_data = user_schema.dump(current_user)
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user_data
        }), 200
        
    except Exception as err:
        db.session.rollback()
        return jsonify({'error': 'Profile update failed', 'details': str(err)}), 500

