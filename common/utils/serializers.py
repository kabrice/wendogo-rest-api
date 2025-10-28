# common/utils/serializers.py
"""
Serializers pour convertir les objets SQLAlchemy en dictionnaires
avec support de l'internationalisation
"""

from common.utils.i18n_helpers import get_localized_field


def domain_to_dict(domain, locale='fr'):
    """
    Convertit un domaine en dictionnaire avec localisation
    """
    return {
        'id': domain.id,
        'name': get_localized_field(domain, 'name', locale),
        'name_en': domain.name_en if hasattr(domain, 'name_en') else None,
        'icon': domain.icon if hasattr(domain, 'icon') else None,
        'program_count': domain.program_count if hasattr(domain, 'program_count') else 0
    }


def subdomain_to_dict(subdomain, locale='fr'):
    """
    Convertit un sous-domaine en dictionnaire avec localisation
    """
    return {
        'id': subdomain.id,
        'name': get_localized_field(subdomain, 'name', locale),
        'name_en': subdomain.name_en if hasattr(subdomain, 'name_en') else None,
        'domain_id': subdomain.domain_id,
        'program_count': subdomain.program_count if hasattr(subdomain, 'program_count') else 0
    }


def program_to_dict(program, locale='fr'):
    """
    Convertit un programme en dictionnaire avec localisation
    """
    # Titre : utilise 'name_en' en anglais, 'title' en français
    if locale == 'en':
        title = get_localized_field(program, 'name', locale) if hasattr(program, 'name_en') else get_localized_field(program, 'title', locale)
    else:
        title = get_localized_field(program, 'title', locale)
    
    result = {
        'id': program.id,
        'title': title,
        'description': get_localized_field(program, 'description', locale),
        'skills_acquired': get_localized_field(program, 'skills_acquired', locale),
        'careers': get_localized_field(program, 'careers', locale),
        'school_id': program.school_id if hasattr(program, 'school_id') else None,
        'school_name': program.school.name if program.school else '',
    }
    
    # Ajouter les champs anglais si disponibles (pour le frontend)
    if hasattr(program, 'name_en'):
        result['name_en'] = program.name_en
    if hasattr(program, 'description_en'):
        result['description_en'] = program.description_en
    if hasattr(program, 'skills_acquired_en'):
        result['skills_acquired_en'] = program.skills_acquired_en
    if hasattr(program, 'careers_en'):
        result['careers_en'] = program.careers_en
    
    # Ajouter les autres champs (pas de localisation nécessaire)
    other_fields = [
        'grade', 'state_certification_type_en', 'state_certification_type_complement_en',
        'duration', 'city', 'alternance_disponible', 'annual_tuition_fees',
        'required_deposit', 'intake', 'application_deadline', 'entry_level',
        'rncp_level', 'language', 'exoneration_totale', 'exoneration_partielle',
        'campus_france_connected', 'parallel_procedure', 'bienvenue_france_level'
    ]
    
    for field in other_fields:
        if hasattr(program, field):
            result[field] = getattr(program, field)
    
    return result


def school_to_dict(school, locale='fr'):
    """
    Convertit une école en dictionnaire (pas de localisation pour les écoles)
    """
    return {
        'id': school.id,
        'name': school.name,
        'city': school.city if hasattr(school, 'city') else None,
        #'type': school.type if hasattr(school, 'type') else None,
        'campus_france_connected': school.campus_france_connected if hasattr(school, 'campus_france_connected') else False
    }
