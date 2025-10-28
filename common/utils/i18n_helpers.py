# common/utils/i18n_helpers.py

# common/utils/i18n_helpers.py
def get_localized_field(obj, field_name, locale='fr'):
    """Retourne le champ selon locale avec fallback"""
    
    if isinstance(obj, dict):
        # En mode anglais, essayer name_en d'abord
        if locale == 'en':
            en_value = obj.get(f"{field_name}_en")
            if en_value:
                return en_value
        
        # Sinon, prendre le champ normal
        fr_value = obj.get(field_name)
        if fr_value:
            return fr_value
        
        # ✅ FALLBACK : Si name est vide, utiliser name_en
        en_value = obj.get(f"{field_name}_en")
        if en_value:
            return en_value
        
        return ''
    
    # Pour objets SQLAlchemy
    if locale == 'en':
        en_value = getattr(obj, f"{field_name}_en", None)
        if en_value:
            return en_value
    
    fr_value = getattr(obj, field_name, None)
    if fr_value:
        return fr_value
    
    # Fallback
    return getattr(obj, f"{field_name}_en", '')


def get_locale_from_request(request):
    """
    Extrait la locale depuis les paramètres de requête
    
    Args:
        request: L'objet Flask request
    
    Returns:
        'fr' ou 'en'
    """
    return request.args.get('locale', 'fr')
