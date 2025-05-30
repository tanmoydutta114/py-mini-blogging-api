
from flask import Blueprint, jsonify, request
from sqlalchemy import desc

from app import db
from app.models import Comment, Post, User
from app.schemas import CommentSchema, CommentCreateSchema
from app.utils.decorators import validate_json, auth_required, paginate_query

# Create blueprint
comments_bp = Blueprint('comments', __name__, url_prefix='/api/comments')


@comments_bp.route('/posts/<int:post_id>', methods=['GET'])
@paginate_query(default_per_page=20, max_per_page=100)
def get_post_comments(post_id: int, page: int, per_page: int) -> tuple:
    try:
        
        post = Post.query.get(post_id)
        if not post or not post.is_published:
            return jsonify({'error': 'Post not found'}), 404
        
        comments_query = Comment.query.filter_by(post_id=post_id).order_by(desc(Comment.created_at))
        
        # Apply pagination
        paginated_comments = comments_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Serialize comments
        comment_schema = CommentSchema(many=True)
        comments_data = comment_schema.dump(paginated_comments.items)
    
        return jsonify({
            'comments': comments_data,
            'post': {
                'id': post.id,
                'title': post.title,
                'slug': post.slug
            },
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated_comments.total,
                'pages': paginated_comments.pages,
                'has_next': paginated_comments.has_next,
                'has_prev': paginated_comments.has_prev
            }
        }), 200
        
    except Exception as err:
        return jsonify({'error': 'Failed to fetch comments', 'details': str(err)}), 500


@comments_bp.route('', methods=['POST'])
@auth_required
@validate_json(CommentCreateSchema)
def create_comment(current_user: User, validated_data: dict) -> tuple:

    try:
        post = Post.query.get(validated_data['post_id'])
        if not post or not post.is_published:
            return jsonify({'error': 'Post not found'}), 404
        
        comment = Comment(
            name=validated_data['name'],
            content=validated_data['content'],
            post_id=validated_data['post_id'],
            author_id=current_user.id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        comment_schema = CommentSchema()
        comment_data = comment_schema.dump(comment)
        
        return jsonify({
            'message': 'Comment created successfully',
            'comment': comment_data
        }), 201
        
    except Exception as err:
        db.session.rollback()
        return jsonify({'error': 'Failed to create comment', 'details': str(err)}), 500


@comments_bp.route('/<int:comment_id>', methods=['GET'])
def get_comment(comment_id: int) -> tuple:

    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        
        comment_schema = CommentSchema()
        comment_data = comment_schema.dump(comment)
        comment_data['author_id'] = comment.author_id
        
        return jsonify({'comment': comment_data}), 200
        
    except Exception as err:
        return jsonify({'error': 'Failed to fetch comment', 'details': str(err)}), 500


@comments_bp.route('/<int:comment_id>', methods=['PUT'])
@auth_required
def update_comment(comment_id: int, current_user: User) -> tuple:

    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        if not comment.can_edit(current_user.id):
            return jsonify({'error': 'Permission denied'}), 403
        
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        if 'name' in json_data:
            if not json_data['name'].strip():
                return jsonify({'error': 'Name cannot be empty'}), 400
            comment.name = json_data['name'].strip()
        
        if 'content' in json_data:
            if not json_data['content'].strip():
                return jsonify({'error': 'Content cannot be empty'}), 400
            comment.content = json_data['content'].strip()
        
        db.session.commit()
        
        comment_schema = CommentSchema()
        comment_data = comment_schema.dump(comment)
        
        return jsonify({
            'message': 'Comment updated successfully',
            'comment': comment_data
        }), 200
        
    except Exception as err:
        db.session.rollback()
        return jsonify({'error': 'Failed to update comment', 'details': str(err)}), 500


@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@auth_required
def delete_comment(comment_id: int, current_user: User) -> tuple:
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404

        if not comment.can_delete(current_user.id):
            return jsonify({'error': 'Permission denied'}), 403

        db.session.delete(comment)
        db.session.commit()

        return jsonify({'message': 'Comment deleted successfully'}), 200

    except Exception as err:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete comment', 'details': str(err)}), 500
