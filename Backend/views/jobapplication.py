from flask import Blueprint, request, jsonify
from app import db
from models import UserJobApplication, User, JobPost
from datetime import datetime

UserJobApplication_bp = Blueprint('UserJobApplication_bp', __name__)

# ---------- CREATE JOB APPLICATION ----------
@UserJobApplication_bp.route('/applications', methods=['POST'])
def create_application():
    data = request.json
    user_id = data.get('user_id')
    job_id = data.get('job_id')

    # Validate presence
    if not user_id or not job_id:
        return jsonify({"error": "user_id and job_id are required"}), 400

    # Check if user and job exist
    user = User.query.get(user_id)
    job = JobPost.query.get(job_id)
    if not user or not job:
        return jsonify({"error": "User or JobPost not found"}), 404

    # Prevent duplicate applications
    existing = UserJobApplication.query.filter_by(user_id=user_id, job_id=job_id).first()
    if existing:
        return jsonify({"error": "You have already applied to this job"}), 409

    application = UserJobApplication(
        user_id=user_id,
        job_id=job_id,
        applied_on=datetime.utcnow(),
        status='Pending'
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({
        "message": "Application submitted",
        "application_id": application.id,
        "applied_on": application.applied_on.isoformat()
    }), 201

# ---------- UPDATE APPLICATION STATUS ----------
@UserJobApplication_bp.route('/applications/<int:application_id>', methods=['PUT'])
def update_application(application_id):
    app = UserJobApplication.query.get_or_404(application_id)
    data = request.json
    new_status = data.get("status")

    if not new_status:
        return jsonify({"error": "Status is required"}), 400

    app.status = new_status
    db.session.commit()
    return jsonify({"message": "Application status updated", "new_status": app.status}), 200

# ---------- GET APPLICATIONS BY USER ----------
@UserJobApplication_bp.route('/applications/user/<int:user_id>', methods=['GET'])
def get_user_applications(user_id):
    apps = UserJobApplication.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "application_id": a.id,
        "job_id": a.job_id,
        "status": a.status,
        "applied_on": a.applied_on.isoformat()
    } for a in apps])

# ---------- DELETE APPLICATION ----------
@UserJobApplication_bp.route('/applications/<int:application_id>', methods=['DELETE'])
def delete_application(application_id):
    app = UserJobApplication.query.get_or_404(application_id)
    db.session.delete(app)
    db.session.commit()
    return jsonify({"message": "Application deleted"}), 200
