from flask import Blueprint, request, jsonify
from app import db
from models import Match, User
from datetime import datetime

Match_bp = Blueprint('Match_bp', __name__)

# ---------- CREATE MATCH ----------
@Match_bp.route('/matches', methods=['POST'])
def create_match():
    data = request.json
    user1_id = data.get('user1_id')
    user2_id = data.get('user2_id')

    # Check required fields
    if not user1_id or not user2_id:
        return jsonify({"error": "user1_id and user2_id are required"}), 400

    # Prevent self-matching
    if user1_id == user2_id:
        return jsonify({"error": "A user cannot match with themselves"}), 400

    # Check if both users exist
    user1 = User.query.get(user1_id)
    user2 = User.query.get(user2_id)
    if not user1 or not user2:
        return jsonify({"error": "One or both users not found"}), 404

    # Prevent duplicate match (regardless of order)
    existing_match = Match.query.filter(
        db.or_(
            db.and_(Match.user1_id == user1_id, Match.user2_id == user2_id),
            db.and_(Match.user1_id == user2_id, Match.user2_id == user1_id)
        )
    ).first()

    if existing_match:
        return jsonify({"error": "Match already exists"}), 409

    match = Match(user1_id=user1_id, user2_id=user2_id, matched_on=datetime.utcnow())
    db.session.add(match)
    db.session.commit()

    return jsonify({
        "message": "Match created",
        "match_id": match.id,
        "user1": user1.name,
        "user2": user2.name,
        "matched_on": match.matched_on.isoformat()
    }), 201

# ---------- GET MATCHES FOR A USER ----------
@Match_bp.route('/matches/<int:user_id>', methods=['GET'])
def get_matches(user_id):
    matches = Match.query.filter(
        db.or_(
            Match.user1_id == user_id,
            Match.user2_id == user_id
        )
    ).all()

    result = []
    for match in matches:
        other_user = match.user2 if match.user1_id == user_id else match.user1
        result.append({
            "match_id": match.id,
            "matched_with": {
                "id": other_user.id,
                "name": other_user.name,
                "profile_image_url": other_user.profile_image_url,
                "course": other_user.course,
                "hobbies": other_user.hobbies,
                "university": other_user.university
            },
            "matched_on": match.matched_on.isoformat()
        })

    return jsonify({"matches": result})

# ---------- DELETE A MATCH ----------
@Match_bp.route('/matches/<int:match_id>', methods=['DELETE'])
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)
    db.session.delete(match)
    db.session.commit()
    return jsonify({"message": "Match deleted"})
