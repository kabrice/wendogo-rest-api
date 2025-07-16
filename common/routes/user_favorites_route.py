
# ═══════════════════════════════════════════════════════════
# 🔧 CORRECTION 2: MÊME CHOSE POUR user_favorites_route.py
# ═══════════════════════════════════════════════════════════

# 📁 common/routes/user_favorites_route.py - VERSION CORRIGÉE
from flask import request, jsonify, current_app
from common.models.user import User
from common.models.user_favorite import UserFavorite
from common.models.program import Program
from common.models import db
from functools import wraps
import jwt

# ✅ DÉFINIR require_auth DANS CE FICHIER AUSSI
def require_auth(f):
    """Décorateur pour vérifier l'authentification"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer TOKEN
            except IndexError:
                return jsonify({'error': 'Token format invalide'}), 401
        
        if not token:
            return jsonify({'error': 'Token manquant'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'Utilisateur non trouvé'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token invalide'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def init_routes(app):
    
    @app.route('/api/user/favorites', methods=['GET'])
    @require_auth
    def get_user_favorites(current_user):
        """Récupérer les favoris de l'utilisateur"""
        try:
            favorites = UserFavorite.query.filter_by(user_id=current_user.id).all()
            program_ids = [fav.program_id for fav in favorites]
            
            return jsonify({
                'success': True,
                'program_ids': program_ids,
                'count': len(program_ids)
            })
            
        except Exception as e:
            print(f"Erreur get favorites: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/user/favorites', methods=['POST'])
    @require_auth
    def add_favorite(current_user):
        """Ajouter un programme aux favoris"""
        try:
            data = request.json
            program_id = data.get('program_id')
            
            if not program_id:
                return jsonify({'success': False, 'error': 'program_id requis'}), 400
            
            # Vérifier si le programme existe
            program = Program.query.filter_by(id=program_id).first()
            if not program:
                return jsonify({'success': False, 'error': 'Programme non trouvé'}), 404
            
            # Vérifier si déjà en favori
            existing = UserFavorite.query.filter_by(
                user_id=current_user.id,
                program_id=program_id
            ).first()
            
            if existing:
                return jsonify({'success': True, 'message': 'Déjà en favori'})
            
            # Ajouter aux favoris
            favorite = UserFavorite(
                user_id=current_user.id,
                program_id=program_id
            )
            
            db.session.add(favorite)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Ajouté aux favoris'
            })
            
        except Exception as e:
            print(f"Erreur add favorite: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/user/favorites', methods=['DELETE'])
    @require_auth
    def remove_favorite(current_user):
        """Retirer un programme des favoris"""
        try:
            data = request.json
            program_id = data.get('program_id')
            
            if not program_id:
                return jsonify({'success': False, 'error': 'program_id requis'}), 400
            
            # Trouver et supprimer le favori
            favorite = UserFavorite.query.filter_by(
                user_id=current_user.id,
                program_id=program_id
            ).first()
            
            if favorite:
                db.session.delete(favorite)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Retiré des favoris'})
            else:
                return jsonify({'success': False, 'error': 'Favori non trouvé'}), 404
                
        except Exception as e:
            print(f"Erreur remove favorite: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/user/favorites/programs', methods=['GET'])
    @require_auth
    def get_favorite_programs(current_user):
        """Récupérer les programmes favoris complets avec détails"""
        try:
            # Jointure pour récupérer les programmes favoris avec leurs détails
            favorites_query = (db.session.query(UserFavorite, Program)
                             .join(Program, UserFavorite.program_id == Program.id)
                             .filter(UserFavorite.user_id == current_user.id)
                             .filter(Program.is_active == True)
                             .order_by(UserFavorite.created_at.desc()))
            
            favorites = favorites_query.all()
            
            programs = []
            for favorite, program in favorites:
                program_data = program.as_dict_with_subdomains()
                if program.school:
                    program_data['school'] = program.school.as_dict()
                program_data['favorited_at'] = favorite.created_at.isoformat()
                programs.append(program_data)
            
            return jsonify({
                'success': True,
                'programs': programs,
                'count': len(programs)
            })
            
        except Exception as e:
            print(f"Erreur get favorite programs: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # @app.route('/api/user/profile', methods=['GET'])
    # @require_auth
    # def get_user_profile(current_user):
    #     """Récupérer le profil utilisateur"""
    #     try:
    #         return jsonify({
    #             'success': True,
    #             'user': {
    #                 'id': current_user.id,
    #                 'email': current_user.email,
    #                 'firstname': current_user.firstname,
    #                 'lastname': current_user.lastname,
    #                 'avatar_url': current_user.avatar_url,
    #                 'provider': current_user.provider,
    #                 'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
    #                 'last_login': current_user.last_login.isoformat() if current_user.last_login else None
    #             }
    #         })
            
    #     except Exception as e:
    #         print(f"Erreur get profile: {e}")
    #         return jsonify({'success': False, 'error': str(e)}), 500
