# common/routes/forum_route.py

from flask import jsonify, request
from common.models import db
from common.models.forum_question import ForumQuestion
from common.models.forum_answer import ForumAnswer
from common.models.forum_question_like import ForumQuestionLike
from common.models.forum_answer_like import ForumAnswerLike
from common.models.user import User
from flask import current_app
import jwt
from functools import wraps

from sqlalchemy import func, desc
import re

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

def optional_auth(f):
    """Décorateur pour l'authentification optionnelle"""
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
                data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                current_user = User.query.get(data['user_id'])
            except Exception as e:
                # ⚠️ IMPORTANT : Ne pas retourner d'erreur, juste passer current_user = None
                print(f"⚠️ Token invalide (optionnel) : {e}")
                pass
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def slugify(text):
    """Crée un slug SEO-friendly"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:100]


def init_routes(app):
    
    # ===== QUESTIONS =====
    
    @app.route('/api/forum/questions', methods=['GET'])
    @optional_auth
    def get_forum_questions(current_user=None):
        """Liste paginée des questions avec filtres et catégories"""
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            category = request.args.get('category', 'all')
            search = request.args.get('search', '')
            sort_by = request.args.get('sort', 'recent')
            
            # Base query
            query = ForumQuestion.query.filter_by(is_active=True)
            
            # Filtre par catégorie
            if category != 'all':
                query = query.filter_by(category=category)
            
            # Recherche
            if search:
                search_term = f'%{search}%'
                query = query.filter(
                    db.or_(
                        ForumQuestion.title.ilike(search_term),
                        ForumQuestion.content.ilike(search_term)
                    )
                )
            
            # Tri
            if sort_by == 'recent':
                query = query.order_by(ForumQuestion.created_at.desc())
            elif sort_by == 'popular':
                # Tri par nombre de likes
                query = query.outerjoin(ForumQuestionLike)\
                    .group_by(ForumQuestion.id)\
                    .order_by(desc(func.count(ForumQuestionLike.id)))
            elif sort_by == 'unanswered':
                # Questions sans réponse
                query = query.outerjoin(ForumAnswer)\
                    .group_by(ForumQuestion.id)\
                    .having(func.count(ForumAnswer.id) == 0)\
                    .order_by(ForumQuestion.created_at.desc())
            elif sort_by == 'answered':
                # Questions avec réponses
                query = query.join(ForumAnswer)\
                    .group_by(ForumQuestion.id)\
                    .having(func.count(ForumAnswer.id) > 0)\
                    .order_by(ForumQuestion.created_at.desc())
            
            # Pagination
            pagination = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            current_user_id = current_user.id if current_user else None
            
            questions_data = [
                q.to_dict(current_user_id=current_user_id) 
                for q in pagination.items
            ]
            
            # Statistiques par catégorie
            categories_stats = db.session.query(
                ForumQuestion.category,
                func.count(ForumQuestion.id).label('count')
            ).filter_by(is_active=True)\
             .group_by(ForumQuestion.category)\
             .all()
            
            return jsonify({
                'success': True,
                'questions': questions_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                },
                'categories_stats': [
                    {'category': cat, 'count': count} 
                    for cat, count in categories_stats
                ],
                'total_questions': ForumQuestion.query.filter_by(is_active=True).count()
            })
            
        except Exception as e:
            print(f"❌ Erreur get_forum_questions: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/forum/questions/<int:question_id>', methods=['GET'])
    @app.route('/api/forum/questions/<int:question_id>/<slug>', methods=['GET'])
    @optional_auth
    def get_forum_question_detail(current_user=None, question_id=None, slug=None):
        """Détail d'une question avec ses réponses + incrémente les vues"""
        try:
            question = ForumQuestion.query.filter_by(
                id=question_id, 
                is_active=True
            ).first_or_404()
            
            # Incrémenter le compteur de vues
            question.views_count += 1
            db.session.commit()
            
            current_user_id = current_user.id if current_user else None
            
            # Charger les réponses
            answers = ForumAnswer.query.filter_by(
                question_id=question_id,
                is_active=True
            ).order_by(
                ForumAnswer.is_accepted.desc(),  # Réponse acceptée en premier
                ForumAnswer.created_at.asc()
            ).all()
            
            return jsonify({
                'success': True,
                'question': question.to_dict(current_user_id=current_user_id),
                'answers': [a.to_dict(current_user_id) for a in answers],
                'can_delete': current_user and question.user_id == current_user_id
            })
            
        except Exception as e:
            print(f"❌ Erreur get_forum_question_detail: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/forum/questions', methods=['POST'])
    @require_auth
    def create_forum_question(current_user):
        """Créer une question (anonyme par défaut)"""
        try:
            data = request.get_json()
            
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            category = data.get('category', 'general')
            
            if not title or len(title) < 10:
                return jsonify({
                    'success': False, 
                    'error': 'Le titre doit contenir au moins 10 caractères'
                }), 400
            
            if not content or len(content) < 20:
                return jsonify({
                    'success': False, 
                    'error': 'La question doit contenir au moins 20 caractères'
                }), 400
            
            # Générer le slug
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            
            # S'assurer que le slug est unique
            while ForumQuestion.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            question = ForumQuestion(
                user_id=current_user.id,
                title=title,
                content=content,
                category=category,
                slug=slug
            )
            
            db.session.add(question)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Question publiée avec succès (anonymement)',
                'question': question.to_dict(current_user_id=current_user.id)
            })
            
        except Exception as e:
            print(f"❌ Erreur create_forum_question: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/forum/questions/<int:question_id>/like', methods=['POST'])
    @require_auth
    def toggle_question_like(current_user, question_id):
        """Liker/unliker une question"""
        try:
            question = ForumQuestion.query.get_or_404(question_id)
            
            existing_like = ForumQuestionLike.query.filter_by(
                question_id=question_id,
                user_id=current_user.id
            ).first()
            
            if existing_like:
                db.session.delete(existing_like)
                action = 'unliked'
            else:
                new_like = ForumQuestionLike(
                    question_id=question_id,
                    user_id=current_user.id
                )
                db.session.add(new_like)
                action = 'liked'
            
            db.session.commit()
            
            likes_count = ForumQuestionLike.query.filter_by(
                question_id=question_id
            ).count()
            
            return jsonify({
                'success': True,
                'action': action,
                'likes_count': likes_count
            })
            
        except Exception as e:
            print(f"❌ Erreur toggle_question_like: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    # ===== RÉPONSES =====
    
    @app.route('/api/forum/questions/<int:question_id>/answers', methods=['POST'])
    @require_auth
    def create_forum_answer(current_user, question_id):
        """Créer une réponse (anonyme par défaut)"""
        try:
            question = ForumQuestion.query.get_or_404(question_id)
            
            data = request.get_json()
            content = data.get('content', '').strip()
            
            if not content or len(content) < 10:
                return jsonify({
                    'success': False,
                    'error': 'La réponse doit contenir au moins 10 caractères'
                }), 400
            
            answer = ForumAnswer(
                question_id=question_id,
                user_id=current_user.id,
                content=content
            )
            
            db.session.add(answer)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Réponse publiée avec succès (anonymement)',
                'answer': answer.to_dict(current_user_id=current_user.id)
            })
            
        except Exception as e:
            print(f"❌ Erreur create_forum_answer: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/forum/answers/<int:answer_id>/like', methods=['POST'])
    @require_auth
    def toggle_answer_like(current_user, answer_id):
        """Liker/unliker une réponse"""
        try:
            answer = ForumAnswer.query.get_or_404(answer_id)
            
            existing_like = ForumAnswerLike.query.filter_by(
                answer_id=answer_id,
                user_id=current_user.id
            ).first()
            
            if existing_like:
                db.session.delete(existing_like)
                action = 'unliked'
            else:
                new_like = ForumAnswerLike(
                    answer_id=answer_id,
                    user_id=current_user.id
                )
                db.session.add(new_like)
                action = 'liked'
            
            db.session.commit()
            
            likes_count = ForumAnswerLike.query.filter_by(
                answer_id=answer_id
            ).count()
            
            return jsonify({
                'success': True,
                'action': action,
                'likes_count': likes_count
            })
            
        except Exception as e:
            print(f"❌ Erreur toggle_answer_like: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    
    @app.route('/api/forum/answers/<int:answer_id>/accept', methods=['POST'])
    @require_auth
    def accept_answer(current_user, answer_id):
        """Accepter une réponse (seulement l'auteur de la question)"""
        try:
            answer = ForumAnswer.query.get_or_404(answer_id)
            question = ForumQuestion.query.get_or_404(answer.question_id)
            
            # Vérifier que c'est l'auteur de la question
            if question.user_id != current_user.id:
                return jsonify({
                    'success': False,
                    'error': 'Non autorisé'
                }), 403
            
            # Désaccepter toutes les autres réponses
            ForumAnswer.query.filter_by(
                question_id=question.id
            ).update({'is_accepted': False})
            
            # Accepter cette réponse
            answer.is_accepted = True
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Réponse marquée comme acceptée'
            })
            
        except Exception as e:
            print(f"❌ Erreur accept_answer: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
