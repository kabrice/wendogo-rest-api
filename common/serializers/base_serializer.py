# common/serializers/base_serializer.py
"""
Module centralisé pour la sérialisation des modèles avec support i18n
"""

class BaseSerializer:
    """Classe de base pour la sérialisation avec gestion de la locale"""
    
    # @staticmethod
    # def get_locale_from_request(request):
    #     """Extrait la locale depuis la requête"""
    #     # Ordre de priorité : header > query param > cookie > défaut
    #     locale = (
    #         request.headers.get('Accept-Language', '').split(',')[0].split('-')[0] or
    #         request.args.get('locale') or
    #         request.cookies.get('NEXT_LOCALE') or
    #         'fr'
    #     )
    #     return locale if locale in ['fr', 'en'] else 'fr'
    
    @staticmethod
    def get_translated_field(obj, field_name, locale):
        """
        Récupère le champ traduit si disponible
        
        Args:
            obj: L'objet modèle
            field_name: Le nom du champ de base (ex: 'name')
            locale: La locale ('fr' ou 'en')
            
        Returns:
            La valeur traduite ou la valeur par défaut
        """
        if locale == 'en':
            en_field = f"{field_name}_en"
            # Retourner le champ EN si existe et non vide, sinon le champ FR
            return getattr(obj, en_field, None) or getattr(obj, field_name, None)
        return getattr(obj, field_name, None)
