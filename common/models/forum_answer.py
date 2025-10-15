# common/models/forum_answer.py
from datetime import datetime
from . import db

class ForumAnswer(db.Model):
    __tablename__ = 'forum_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('forum_questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_accepted = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = db.relationship('User', backref='forum_answers')
    likes = db.relationship('ForumAnswerLike', backref='answer', lazy='dynamic', cascade='all, delete-orphan')
    
    
    def to_dict(self, current_user_id=None):
        """Convertit en dict avec gestion de l'anonymat"""
        MODERATOR_IDS = [608, 605]
        is_moderator = self.user_id in MODERATOR_IDS
        
        data = {
            'id': self.id,
            'question_id': self.question_id,
            'content': self.content,
            'is_accepted': self.is_accepted,
            'likes_count': self.likes.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_moderator': is_moderator,
            'author_name': 'Modérateur Wendogo' if is_moderator else 'Utilisateur anonyme',
            'is_liked': False
        }
        
        if current_user_id:
            data['is_liked'] = self.likes.filter_by(user_id=current_user_id).first() is not None
            data['is_author'] = (self.user_id == current_user_id)
        
        return data
