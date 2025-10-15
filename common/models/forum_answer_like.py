from dataclasses import dataclass
from datetime import datetime
from . import db

@dataclass
class ForumAnswerLike(db.Model):
    __tablename__ = 'forum_answer_likes'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('forum_answers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relations
    user = db.relationship('User', backref=db.backref('forum_answer_likes', lazy=True))
    
    # Contrainte d'unicité
    __table_args__ = (
        db.UniqueConstraint('answer_id', 'user_id', name='unique_answer_like'),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f'<ForumAnswerLike {self.id}>'
