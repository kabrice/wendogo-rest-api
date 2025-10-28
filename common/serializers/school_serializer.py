# common/serializers/school_serializer.py
"""
Serializer pour les écoles avec support multilingue
"""
from .base_serializer import BaseSerializer

class SchoolSerializer(BaseSerializer):
    """Sérialisation des écoles avec gestion i18n"""
    
    @classmethod
    def serialize(cls, school, locale='fr', include_programs=False):
        """
        Sérialise une école selon la locale
        
        Args:
            school: Instance du modèle School
            locale: 'fr' ou 'en'
            include_programs: Inclure la liste des programmes
            
        Returns:
            dict: École sérialisée
        """
        
        data = {

            'id': school.id,
            'slug': school.slug,
            'school_group': school.school_group,
            'base_city': school.base_city,
            
            # Coordonnées
            'address': school.address,
            'phone': school.phone,
            'email': school.email,
            'name': school.name,
            'description': cls.get_translated_field(school, 'description', locale),
            
            # Frais et exonérations
            'exoneration_tuition': school.exoneration_tuition,
            'exoneration_tuition_comment': cls.get_translated_field(school, 'exoneration_tuition_comment', locale),
            
            # Statut
            'hors_contrat': school.hors_contrat,
            'acknowledgement': school.acknowledgement,
            
            # Alternance
            'alternance_rate': school.alternance_rate,
            'alternance_comment': school.alternance_comment,
            'alternance_comment_tech': cls.get_translated_field(school, 'alternance_comment_tech', locale),
            'work_study_programs': cls.get_translated_field(school, 'work_study_programs', locale),
            
            # Étudiants internationaux
            'international_student_rate': school.international_student_rate,
            'international_student_rate_tech': school.international_student_rate_tech,
            'international_student_comment': cls.get_translated_field(school, 'international_student_comment', locale),
            'international_student_comment_tech': school.international_student_comment_tech,
            
            # Campus France
            'connection_campus_france': school.connection_campus_france,
            
            # Évaluations
            'rating': str(school.rating) if school.rating else None,
            'reviews_counter': school.reviews_counter,
            
            # URLs et réseaux sociaux
            'url': school.url,
            'facebook_url': school.facebook_url,
            'x_url': school.x_url,
            'linkedin_url': school.linkedin_url,
            'instagram_url': school.instagram_url,
            
            # Rankings
            'national_ranking': cls.get_translated_field(school, 'national_ranking', locale),
            'international_ranking': cls.get_translated_field(school, 'international_ranking', locale),

            # Support international
            'international_support_before_coming': cls.get_translated_field(school, 'international_support_before_coming', locale),
            'international_support_after_coming': cls.get_translated_field(school, 'international_support_after_coming', locale),
            
            # Admission et partenariats
            'general_entry_requirements': cls.get_translated_field(school, 'general_entry_requirements', locale),
            'partnerships': cls.get_translated_field(school, 'partnerships', locale),
            'facilities': cls.get_translated_field(school, 'facilities', locale),

            # # Visibilité
            'is_public': school.is_public,
            
            # # SEO
            'seo_title': cls.get_translated_field(school, 'seo_title', locale),
            'seo_description': cls.get_translated_field(school, 'seo_description', locale),
            'seo_keywords': cls.get_translated_field(school, 'seo_keywords', locale),

            # # Médias
            'logo_path': school.logo_path,
            'cover_page_path': school.cover_page_path,
        }
        
        # Inclure les programmes si demandé
        if include_programs and hasattr(school, 'programs'):
            from .program_serializer import ProgramSerializer
            data['programs'] = ProgramSerializer.serialize_many(
                school.programs, 
                locale, 
                include_school=False
            )
        
        return data
    
    @classmethod
    def serialize_many(cls, schools, locale='fr', include_programs=False):
        """Sérialise une liste d'écoles"""
        return [cls.serialize(school, locale, include_programs) for school in schools]
