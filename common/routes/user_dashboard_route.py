# common/routes/user_dashboard_route.py - VERSION MISE À JOUR

from flask import request, jsonify, current_app
from common.models.user import User
from common.models.user_favorite import UserFavorite
from common.models.accompany_request import AccompanyRequest
from common.models.program import Program
from common.models.school import School
from common.models.forum_question import ForumQuestion
from common.models.forum_answer import ForumAnswer
from common.models import db
from sqlalchemy import func, distinct
from functools import wraps
import jwt

def require_auth(f):
    """Décorateur pour vérifier l'authentification"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
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
    
    @app.route('/api/user/dashboard', methods=['GET'])
    @require_auth
    def get_user_dashboard(current_user):
        """Dashboard utilisateur avec statistiques et accompagnement"""
        try:
            # Compter les favoris
            favorites_count = UserFavorite.query.filter_by(user_id=current_user.id).count()
            
            # Récupérer les derniers favoris ajoutés
            recent_favorites = (db.session.query(UserFavorite, Program)
                              .join(Program, UserFavorite.program_id == Program.id)
                              .filter(UserFavorite.user_id == current_user.id)
                              .filter(Program.is_active == True)
                              .order_by(UserFavorite.created_at.desc())
                              .limit(5)
                              .all())
            
            user_questions = ForumQuestion.query.filter_by(
                user_id=current_user.id,
                is_active=True
            ).order_by(ForumQuestion.created_at.desc()).limit(5).all()
            
            questions_data = []
            for q in user_questions:
                # Compter les réponses
                answers_count = ForumAnswer.query.filter_by(
                    question_id=q.id,
                    is_active=True
                ).count()
                
                q_dict = q.to_dict(current_user_id=current_user.id)
                q_dict['answers_count'] = answers_count
                questions_data.append(q_dict)
            
            recent_programs = []
            for favorite, program in recent_favorites:
                program_data = {
                    'id': program.id,
                    'title': program.name,
                    'school_name': program.school_name,
                    'school_logo_path': None,
                    'grade': program.grade,
                    'duration': program.fi_school_duration,
                    'favorited_at': favorite.created_at.isoformat()
                }
                # Fetch school logo_path if available
                school = School.query.filter_by(id=program.school_id).first()
                if school and hasattr(school, 'logo_path'):
                    program_data['school_logo_path'] = school.logo_path
                recent_programs.append(program_data)
            
            # ✅ NOUVEAU: Récupérer les demandes d'accompagnement
            accompany_requests = AccompanyRequest.query.filter_by(
                user_id=current_user.id
            ).order_by(AccompanyRequest.created_at.desc()).limit(3).all()
            
            accompany_data = []
            for request in accompany_requests:
                accompany_data.append({
                    'id': request.id,
                    'offer_name': request.offer_name,
                    'offer_id': request.offer_id,
                    'price': request.price,
                    'currency': request.currency,
                    'status': request.status,
                    'status_label': request.get_status_label(),
                    'urgency': request.urgency,
                    'urgency_label': request.get_urgency_label(),
                    'created_at': request.created_at.isoformat(),
                    'contacted_at': request.contacted_at.isoformat() if request.contacted_at else None,
                    'assigned_counselor': request.assigned_counselor
                })
            
            # ✅ NOUVEAU: Statistiques d'accompagnement
            total_requests = len(accompany_requests)
            pending_requests = len([r for r in accompany_requests if r.status == 'pending'])
            completed_requests = len([r for r in accompany_requests if r.status == 'completed'])
            
            # Statistiques par domaine des favoris
            domain_stats = (db.session.query(
                                Program.sub_domain1_id.label('subdomain_id'),
                                func.count(UserFavorite.id).label('count')
                            )
                           .join(UserFavorite, Program.id == UserFavorite.program_id)
                           .filter(UserFavorite.user_id == current_user.id)
                           .group_by(Program.sub_domain1_id)
                           .order_by(func.count(UserFavorite.id).desc())
                           .limit(5)
                           .all())
            
            # ✅ NOUVEAU: Recommandations personnalisées basées sur l'accompagnement
            recommendations = []
            if accompany_requests:
                latest_request = accompany_requests[0]
                if latest_request.offer_id == 'orientation':
                    recommendations.append({
                        'type': 'next_step',
                        'title': 'Préparez votre dossier',
                        'description': 'Maintenant que vous avez choisi vos formations, préparez votre dossier Campus France.',
                        'action': 'Voir le Pack Visa',
                        'link': '/accompagnement#visa'
                    })
                elif latest_request.offer_id == 'visa':
                    recommendations.append({
                        'type': 'next_step',
                        'title': 'Préparez votre installation',
                        'description': 'Une fois votre visa obtenu, préparez votre arrivée en France.',
                        'action': 'Voir le Pack Installation',
                        'link': '/accompagnement#installation'
                    })
            
            return jsonify({
                'success': True,
                'dashboard': {
                    'user': {
                        'firstname': current_user.firstname,
                        'lastname': current_user.lastname,
                        'avatar_url': current_user.avatar_url,
                        'email': current_user.email,
                        'country': current_user.country
                    },
                    'statistics': {
                        'favorites_count': favorites_count,
                        'accompany_requests_count': total_requests,
                        'pending_requests_count': pending_requests,
                        'completed_requests_count': completed_requests,
                        'questions_count': len(questions_data),
                        'last_login': current_user.last_login.isoformat() if current_user.last_login else None
                    },
                    'recent_favorites': recent_programs,
                    'domain_preferences': [
                        {'subdomain_id': stat.subdomain_id, 'count': stat.count}
                        for stat in domain_stats
                    ],
                    'user_questions': questions_data,
                    # ✅ NOUVELLES SECTIONS
                    'accompany_requests': accompany_data,
                    'recommendations': recommendations,
                    'quick_actions': [
                        {
                            'type': 'favorites',
                            'title': 'Mes Favoris',
                            'description': f'{favorites_count} formation(s) sauvegardée(s)',
                            'link': '/favorites',
                            'icon': 'heart'
                        },
                        {
                            'type': 'search',
                            'title': 'Rechercher',
                            'description': 'Trouvez de nouvelles formations',
                            'link': '/',
                            'icon': 'search'
                        },
                        {
                            'type': 'accompany',
                            'title': 'Accompagnement',
                            'description': 'Bénéficiez d\'un accompagnement personnalisé',
                            'link': '/accompagnement',
                            'icon': 'graduation-cap'
                        }
                    ]
                }
            })
            
        except Exception as e:
            print(f"Erreur dashboard: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/accompany-requests', methods=['GET'])
    def get_admin_accompany_requests():
        """Récupérer toutes les demandes d'accompagnement pour l'admin"""
        try:
            requests = (AccompanyRequest.query
                       .join(User, AccompanyRequest.user_id == User.id)
                       .order_by(AccompanyRequest.created_at.desc())
                       .all())
            
            requests_data = []
            for request in requests:
                request_dict = request.as_dict()
                request_dict['user'] = {
                    'id': request.user.id,
                    'firstname': request.user.firstname,
                    'lastname': request.user.lastname,
                    'email': request.user.email,
                    'phone': request.user.phone,
                    'country': request.user.country
                }
                requests_data.append(request_dict)
            
            return jsonify({
                'success': True,
                'requests': requests_data
            })
            
        except Exception as e:
            print(f"Erreur get_admin_accompany_requests: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/organization-contacts', methods=['GET'])
    def get_admin_organization_contacts():
        """Récupérer tous les contacts d'organismes pour l'admin"""
        try:
            from common.models.organization_contact import OrganizationContact
            
            contacts = (OrganizationContact.query
                       .order_by(OrganizationContact.created_at.desc())
                       .all())
            
            return jsonify({
                'success': True,
                'contacts': [contact.as_dict() for contact in contacts]
            })
            
        except Exception as e:
            print(f"Erreur get_admin_organization_contacts: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/accompany-requests/<int:request_id>', methods=['PATCH'])
    def update_accompany_request_status(request_id):
        """Mettre à jour le statut d'une demande d'accompagnement"""
        try:
            data = request.json
            new_status = data.get('status')
            
            if not new_status:
                return jsonify({'success': False, 'error': 'Statut requis'}), 400
            
            accompany_request = AccompanyRequest.query.get_or_404(request_id)
            accompany_request.status = new_status
            
            # Mettre à jour la date de contact si le statut passe à "contacted"
            if new_status == 'contacted' and not accompany_request.contacted_at:
                accompany_request.contacted_at = db.func.current_timestamp()
            
            # Mettre à jour le statut de l'utilisateur
            user = User.query.get(accompany_request.user_id)
            if user:
                user.accompany_status = new_status
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Statut mis à jour avec succès'
            })
            
        except Exception as e:
            print(f"Erreur update_accompany_request_status: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
