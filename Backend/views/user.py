from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app import db
from models import User
from datetime import datetime

User_bp = Blueprint('User_bp', __name__)

# ---------- CREATE USER ----------
@User_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json

    required_fields = ['email', 'password', 'name']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 409

    hashed_password = generate_password_hash(data['password'])

    user = User(
        email=data['email'],
        password=hashed_password,
        name=data['name'],
        university=data.get('university'),
        course=data.get('course'),
        hobbies=data.get('hobbies'),
        height=data.get('height'),
        profile_image_url=data.get('profile_image_url'),
        bio=data.get('bio'),
        gender=data.get('gender'),
        created_at=datetime.utcnow()
    )

    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created", "user_id": user.id}), 201

# ---------- GET USER ----------
@User_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "university": user.university,
        "course": user.course,
        "hobbies": user.hobbies,
        "height": user.height,
        "profile_image_url": user.profile_image_url,
        "bio": user.bio,
        "gender": user.gender,
        "created_at": user.created_at.isoformat()
    })

# ---------- UPDATE USER ----------
@User_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json

    if 'password' in data:
        user.password = generate_password_hash(data['password'])

    for field in ['email', 'name', 'university', 'course', 'hobbies', 'height', 'profile_image_url', 'bio', 'gender']:
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()
    return jsonify({"message": "User updated successfully"})

# ---------- DELETE USER ----------
@User_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})
