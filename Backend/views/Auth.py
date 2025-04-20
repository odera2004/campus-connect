from flask import jsonify, request, Blueprint
from models import db, User,TokenBlocklist
from flask_jwt_extended import jwt_required,get_jwt_identity,get_jwt,create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import datetime,timezone
# from app import Mail, Message
import os

auth_bp = Blueprint('auth', __name__)

# Initialize serializer for password reset
serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY", "fallback-secret-key"))

# Configure Flask-Mail
# mail = Mail()

#Login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if email and password are provided
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Query the database for the user
    user = User.query.filter_by(email=email).first()

    # Check if the user exists and the password is correct
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        user_data = {
            "id": user.id,
            "email": user.email
        }

        return jsonify({
            "access_token": access_token,
            "user": user_data 
        }), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401
    
#Login with google 
@auth_bp.route('/login_with_google', methods= ['POST'])
def login_with_google():
    data = request.get_json()
    email = data.get('email')

    # Check if email is provided
    if not email :
        return jsonify({"error": "Email is required"}), 400

    # Query the database for the user
    user = User.query.filter_by(email=email).first()

    if user:
        # Create access token
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"error": "User not found "}), 404
    
# current user
@auth_bp.route('/current_user', methods=['GET'])
@jwt_required()
def current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {
        'id': user.id,
        'username' : user.username,
        'email': user.email,
        'password' : user.password,
        'role': user.role  
    }
    return jsonify(user_data), 200

@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # JWT ID
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify({"success": "Logged out successfully"}), 200

# Forgot Password
# @auth_bp.route('/forgot-password', methods=['POST'])
# def forgot_password():
#     data = request.get_json()
#     email = data.get('email')

#     if not email:
#         return jsonify({"error": "Email is required"}), 400

#     user = User.query.filter_by(email=email).first()
#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     token = serializer.dumps(email, salt="password-reset")
#     reset_link = f"http://localhost:5173/reset-password/{token}"

#     msg = Message("Password Reset Request", sender="noreply@example.com", recipients=[email])
#     msg.body = f"Click the link to reset your password: {reset_link}"

#     try:
#         mail.send(msg)
#     except Exception as e:
#         print(f"Error sending email: {e}")
#         return jsonify({"error": "Failed to send email"}), 500

#     return jsonify({"message": "Password reset email sent"}), 200

# Reset Password
@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    data = request.get_json()
    new_password = data.get('password')

    if not new_password:
        return jsonify({"error": "Password is required"}), 400

    try:
        email = serializer.loads(token, salt="password-reset", max_age=1800)  # 30 min expiry
    except SignatureExpired:
        return jsonify({"error": "Token has expired"}), 400
    except BadSignature:
        return jsonify({"error": "Invalid token"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Password reset successful"}), 200