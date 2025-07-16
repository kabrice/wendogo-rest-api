# ═══════════════════════════════════════════════════════════
# 🐍 BACKEND FLASK - AUTHENTIFICATION ET FAVORIS
# ═══════════════════════════════════════════════════════════

# 📁 common/models/user_favorite.py (NOUVEAU MODÈLE)
from common.models import db
from dataclasses import dataclass
from datetime import datetime

@dataclass
class UserFavorite(db.Model):
    __tablename__ = 'user_favorites'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    program_id = db.Column(db.String(10), nullable=False)  # ID du programme
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Index unique pour éviter les doublons
    __table_args__ = (
        db.UniqueConstraint('user_id', 'program_id', name='unique_user_program_favorite'),
    )

    def as_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'program_id': self.program_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
