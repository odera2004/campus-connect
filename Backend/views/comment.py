from flask import Blueprint, request, jsonify
from app import db
from models import Comment, User, ForumPost
from datetime import datetime

Comment_bp = Blueprint('Comment_bp', __name__)

@Comment_bp.route('/comments', methods=['POST'])
def create_comment():
    data = request.json
    required_fields = ['content', 'user_id', 'post_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if not User.query.get(data['user_id']):
        return jsonify({'error': 'User not found'}), 404

    if not ForumPost.query.get(data['post_id']):
        return jsonify({'error': 'Forum post not found'}), 404

    comment = Comment(
        content=data['content'],
        user_id=data['user_id'],
        post_id=data['post_id'],
        created_at=datetime.utcnow()
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({"message": "Comment created", "comment_id": comment.id}), 201

@Comment_bp.route('/comments/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return jsonify({
        "id": comment.id,
        "content": comment.content,
        "user_id": comment.user_id,
        "post_id": comment.post_id,
        "created_at": comment.created_at.isoformat()
    })

@Comment_bp.route('/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    data = request.json
    if "content" in data:
        comment.content = data["content"]
    db.session.commit()
    return jsonify({"message": "Comment updated"})

@Comment_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message": "Comment deleted"})

@Comment_bp.route('/comments/post/<int:post_id>', methods=['GET'])
def get_comments_by_post(post_id):
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
    return jsonify([
        {
            "id": c.id,
            "content": c.content,
            "user_id": c.user_id,
            "created_at": c.created_at.isoformat()
        } for c in comments
    ])
