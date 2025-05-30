
from flask import Blueprint, jsonify, request
from sqlalchemy import desc

from app import db
from app.models import Post, User
from app.schemas import PostSchema, PostCreateSchema, PostUpdateSchema, PostListSchema
from app.utils.decorators import validate_json, auth_required, paginate_query

# Create blueprint
posts_bp = Blueprint('posts', __name__, url_prefix='/api/posts')


@posts_bp.route('', methods=['GET'])
@paginate_query(default_per_page=10, max_per_page=50)
def get_posts(page: int, per_page: int) -> tuple:
    try:
        posts_query = Post.query.filter_by(is_published=True).order_by(desc(Post.created_at))
        paginated_posts = posts_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        post_schema = PostListSchema(many=True)
        posts_data = post_schema.dump(paginated_posts.items)
        
        return jsonify({
            'posts': posts_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated_posts.total,
                'pages': paginated_posts.pages,
                'has_next': paginated_posts.has_next,
                'has_prev': paginated_posts.has_prev
            }
        }), 200
        
    except Exception as err:
        return jsonify({'error': 'Failed to fetch posts', 'details': str(err)}), 500


@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id: int) -> tuple:
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        if not post.is_published:
            return jsonify({'error': 'Post not found'}), 404
        
        post_schema = PostSchema()
        post_data = post_schema.dump(post)
        post_data['author_id'] = post.author_id
        
        return jsonify({'post': post_data}), 200
        
    except Exception as err:
        return jsonify({'error': 'Failed to fetch post', 'details': str(err)}), 500


@posts_bp.route('', methods=['POST'])
@auth_required
@validate_json(PostCreateSchema)
def create_post(current_user: User, validated_data: dict) -> tuple:
    try:
        post = Post(
            title=validated_data['title'],
            content=validated_data['content'],
            author_id=current_user.id,
            is_published=validated_data.get('is_published', True)
        )
        
        db.session.add(post)
        db.session.commit()
        
        post_schema = PostSchema()
        post_data = post_schema.dump(post)
        print(f"Post created: {post_data['title']} by {current_user.username}")
        return jsonify({
            'message': 'Post created successfully',
            'post': post_data
        }), 201
        
    except Exception as err:
        print(err)
        db.session.rollback()
        return jsonify({'error': 'Failed to create post', 'details': str(err)}), 500


@posts_bp.route('/<int:post_id>', methods=['PUT'])
@auth_required
@validate_json(PostUpdateSchema)
def update_post(post_id: int, current_user: User, validated_data: dict) -> tuple:
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        if not post.can_edit(current_user.id):
            return jsonify({'error': 'Permission denied'}), 403
        
        if 'title' in validated_data:
            post.title = validated_data['title']
            post.slug = post._generate_slug(validated_data['title'])
        
        if 'content' in validated_data:
            post.content = validated_data['content']
        
        if 'is_published' in validated_data:
            post.is_published = validated_data['is_published']
        
        db.session.commit()
        
        post_schema = PostSchema()
        post_data = post_schema.dump(post)
        
        return jsonify({
            'message': 'Post updated successfully',
            'post': post_data
        }), 200
        
    except Exception as err:
        db.session.rollback()
        return jsonify({'error': 'Failed to update post', 'details': str(err)}), 500


@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@auth_required
def delete_post(post_id: int, current_user: User) -> tuple:
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        if not post.can_delete(current_user.id):
            return jsonify({'error': 'Permission denied'}), 403
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({
            'message': 'Post deleted successfully'
        }), 200
        
    except Exception as err:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete post', 'details': str(err)}), 500

