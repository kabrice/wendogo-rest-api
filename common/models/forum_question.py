# common/models/forum_question.py
from datetime import datetime
from . import db

class ForumQuestion(db.Model):
    __tablename__ = 'forum_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(600), unique=True, nullable=False)  # Pour SEO
    views_count = db.Column(db.Integer, default=0)
    is_resolved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = db.relationship('User', backref='forum_questions')
    answers = db.relationship('ForumAnswer', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('ForumQuestionLike', backref='question', lazy='dynamic', cascade='all, delete-orphan')

    
    
    def to_dict(self, include_user=False, current_user_id=None):
        """
        Convertit en dict avec gestion de l'anonymat
        Seuls les modérateurs (user_id 608, 605) peuvent afficher leur nom
        """
        # Liste des modérateurs autorisés à afficher leur nom
        MODERATOR_IDS = [608, 605]
        
        # Déterminer si on affiche le nom
        is_moderator = self.user_id in MODERATOR_IDS
        
        data = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'slug': self.slug,
            'views_count': self.views_count,
            'answers_count': self.answers.filter_by(is_active=True).count(),
            'likes_count': self.likes.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_moderator': is_moderator,
            'author_name': 'Modérateur Wendogo' if is_moderator else 'Utilisateur anonyme',
            'is_liked': False
        }
        
        # Vérifier si l'utilisateur actuel a liké
        if current_user_id:
            data['is_liked'] = self.likes.filter_by(user_id=current_user_id).first() is not None
            data['is_author'] = (self.user_id == current_user_id)
        
        return data
