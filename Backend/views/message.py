from flask import Blueprint, request, jsonify
from app import db
from models import Message, User
from datetime import datetime

Message_bp = Blueprint('Message_bp', __name__)

# ---------- CREATE MESSAGE ----------
@Message_bp.route('/messages', methods=['POST'])
def create_message():
    data = request.json

    # Validate required fields
    for field in ['sender_id', 'receiver_id', 'content']:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    # Optional: Prevent self-messaging
    if data['sender_id'] == data['receiver_id']:
        return jsonify({"error": "Cannot send message to yourself"}), 400

    # Optional: Validate users exist
    sender = User.query.get(data['sender_id'])
    receiver = User.query.get(data['receiver_id'])
    if not sender or not receiver:
        return jsonify({"error": "Sender or receiver not found"}), 404

    message = Message(
        sender_id=data['sender_id'],
        receiver_id=data['receiver_id'],
        content=data['content'],
        timestamp=datetime.utcnow()
    )
    db.session.add(message)
    db.session.commit()

    return jsonify({
        "message": "Message sent",
        "message_id": message.id,
        "timestamp": message.timestamp.isoformat()
    }), 201

# ---------- GET MESSAGES FOR USER ----------
@Message_bp.route('/messages/<int:user_id>', methods=['GET'])
def get_messages(user_id):
    sent = Message.query.filter_by(sender_id=user_id).all()
    received = Message.query.filter_by(receiver_id=user_id).all()

    return jsonify({
        "sent": [{
            "id": m.id,
            "to": m.receiver.name,
            "receiver_id": m.receiver_id,
            "content": m.content,
            "timestamp": m.timestamp.isoformat()
        } for m in sent],
        "received": [{
            "id": m.id,
            "from": m.sender.name,
            "sender_id": m.sender_id,
            "content": m.content,
            "timestamp": m.timestamp.isoformat()
        } for m in received]
    })

# ---------- DELETE MESSAGE ----------
@Message_bp.route('/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    return jsonify({"message": "Message deleted"}), 200
