from flask import Blueprint, request, jsonify
from app import db
from models import ForumPost, User
from datetime import datetime

Forum_bp = Blueprint('Forum_bp', __name__)

@Forum_bp.route('/forum-posts', methods=['POST'])
def create_forum_post():
    data = request.json
    required_fields = ['title', 'content', 'user_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if not User.query.get(data['user_id']):
        return jsonify({'error': 'User not found'}), 404

    post = ForumPost(
        title=data['title'],
        content=data['content'],
        tag=data.get('tag'),
        university=data.get('university'),
        user_id=data['user_id'],
        created_at=datetime.utcnow()
    )
    db.session.add(post)
    db.session.commit()
    return jsonify({'message': 'Forum post created', 'post_id': post.id}), 201

@Forum_bp.route('/forum-posts/<int:post_id>', methods=['GET'])
def get_forum_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    return jsonify({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'tag': post.tag,
        'university': post.university,
        'user_id': post.user_id,
        'created_at': post.created_at.isoformat()
    })

@Forum_bp.route('/forum-posts/<int:post_id>', methods=['PUT'])
def update_forum_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    data = request.json
    for key in ['title', 'content', 'tag', 'university']:
        if key in data:
            setattr(post, key, data[key])
    db.session.commit()
    return jsonify({'message': 'Forum post updated'})

@Forum_bp.route('/forum-posts/<int:post_id>', methods=['DELETE'])
def delete_forum_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Forum post deleted'})

@Forum_bp.route('/forum-posts', methods=['GET'])
def list_forum_posts():
    posts = ForumPost.query.order_by(ForumPost.created_at.desc()).all()
    return jsonify([
        {
            'id': p.id,
            'title': p.title,
            'tag': p.tag,
            'university': p.university,
            'user_id': p.user_id,
            'created_at': p.created_at.isoformat()
        }
        for p in posts
    ])
