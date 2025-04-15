from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.dialects.sqlite import JSON 
from datetime import datetime

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    university = db.Column(db.String(100))  # University Name
    course = db.Column(db.String(100))  # Course/Program
    hobbies = db.Column(db.String(300))  # Hobbies, comma-separated
    height = db.Column(db.String(10))  # Height for dating purposes
    profile_image_url = db.Column(db.String(200))  # URL to the profile image
    bio = db.Column(db.Text)  # Bio/description
    gender = db.Column(db.String(10))  # Gender for matching
    matched_users = db.relationship('Match', backref='user', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.name}>'


class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tag = db.Column(db.String(50))  # Tags for the post (e.g., "Drama Club", "Sports")
    university = db.Column(db.String(100))  # University for filtering
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Author of the post
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='forum_posts', lazy=True)

    def __repr__(self):
        return f'<ForumPost {self.title}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Commenter
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'))  # Associated forum post
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='comments', lazy=True)
    post = db.relationship('ForumPost', backref='comments', lazy=True)

    def __repr__(self):
        return f'<Comment {self.id}>'


class JobPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company_name = db.Column(db.String(100))  # Company/Organization offering
    location = db.Column(db.String(100))  # Job location
    type = db.Column(db.String(50))  # Type of opportunity (e.g., Internship, Full-time)
    university = db.Column(db.String(100))  # Which university students are targeted
    deadline = db.Column(db.Date)  # Application deadline
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # Who posted the job
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='job_posts', lazy=True)

    def __repr__(self):
        return f'<JobPost {self.title}>'

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # First user
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Second user
    matched_on = db.Column(db.DateTime, default=datetime.utcnow)  # Date of match

    user1 = db.relationship('User', foreign_keys=[user1_id], backref='matches_user1')
    user2 = db.relationship('User', foreign_keys=[user2_id], backref='matches_user2')

    def __repr__(self):
        return f'<Match {self.user1_id} & {self.user2_id}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Sender of the message
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Receiver of the message
    content = db.Column(db.Text)  # Content of the message
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # When message was sent

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def __repr__(self):
        return f'<Message {self.id}>'


class UserJobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Student applying
    job_id = db.Column(db.Integer, db.ForeignKey('job_post.id'))  # Job post being applied to
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)  # Date of application
    status = db.Column(db.String(50), default="Pending")  # Application status (e.g., Pending, Accepted, Rejected)
    
    user = db.relationship('User', backref='job_applications', lazy=True)
    job = db.relationship('JobPost', backref='applications', lazy=True)

    def __repr__(self):
        return f'<Application {self.user_id} for Job {self.job_id}>'


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)