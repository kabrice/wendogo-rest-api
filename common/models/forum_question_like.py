from dataclasses import dataclass
from datetime import datetime
from . import db

@dataclass
class ForumQuestionLike(db.Model):
    __tablename__ = 'forum_question_likes'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('forum_questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relations
    user = db.relationship('User', backref=db.backref('forum_question_likes', lazy=True))
    
    # Contrainte d'unicité
    __table_args__ = (
        db.UniqueConstraint('question_id', 'user_id', name='unique_question_like'),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f'<ForumQuestionLike {self.id}>'
