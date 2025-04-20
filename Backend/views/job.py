from flask import Blueprint, request, jsonify
from app import db
from models import JobPost, User
from datetime import datetime

JobPost_bp = Blueprint('JobPost_bp', __name__)

@JobPost_bp.route('/job-posts', methods=['POST'])
def create_job_post():
    data = request.json
    required_fields = ['title', 'description', 'posted_by']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if not User.query.get(data['posted_by']):
        return jsonify({'error': 'Posting user not found'}), 404

    job = JobPost(
        title=data['title'],
        description=data['description'],
        company_name=data.get('company_name'),
        location=data.get('location'),
        type=data.get('type'),
        university=data.get('university'),
        deadline=datetime.strptime(data['deadline'], "%Y-%m-%d") if data.get('deadline') else None,
        posted_by=data['posted_by'],
        created_at=datetime.utcnow()
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({'message': 'Job post created', 'job_id': job.id}), 201

@JobPost_bp.route('/job-posts/<int:job_id>', methods=['GET'])
def get_job_post(job_id):
    job = JobPost.query.get_or_404(job_id)
    return jsonify({
        'id': job.id,
        'title': job.title,
        'description': job.description,
        'company_name': job.company_name,
        'location': job.location,
        'type': job.type,
        'university': job.university,
        'deadline': job.deadline.isoformat() if job.deadline else None,
        'posted_by': job.posted_by,
        'created_at': job.created_at.isoformat()
    })

@JobPost_bp.route('/job-posts/<int:job_id>', methods=['PUT'])
def update_job_post(job_id):
    job = JobPost.query.get_or_404(job_id)
    data = request.json
    for key in ['title', 'description', 'company_name', 'location', 'type', 'university', 'deadline']:
        if key in data:
            if key == 'deadline':
                setattr(job, key, datetime.strptime(data[key], "%Y-%m-%d"))
            else:
                setattr(job, key, data[key])
    db.session.commit()
    return jsonify({'message': 'Job post updated'})

@JobPost_bp.route('/job-posts/<int:job_id>', methods=['DELETE'])
def delete_job_post(job_id):
    job = JobPost.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return jsonify({'message': 'Job post deleted'})

@JobPost_bp.route('/job-posts', methods=['GET'])
def list_job_posts():
    jobs = JobPost.query.order_by(JobPost.created_at.desc()).all()
    return jsonify([
        {
            'id': job.id,
            'title': job.title,
            'type': job.type,
            'company_name': job.company_name,
            'location': job.location,
            'university': job.university,
            'deadline': job.deadline.isoformat() if job.deadline else None
        }
        for job in jobs
    ])
