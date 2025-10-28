# common/serializers/program_serializer.py
"""
Serializer pour les programmes avec support multilingue
"""
from .base_serializer import BaseSerializer

class ProgramSerializer(BaseSerializer):
    """Sérialisation des programmes avec gestion i18n"""
    
    @classmethod
    def serialize(cls, program, locale='fr', include_school=True):
        """
        Sérialise un programme selon la locale
        
        Args:
            program: Instance du modèle Program
            locale: 'fr' ou 'en'
            include_school: Inclure les détails de l'école
            
        Returns:
            dict: Programme sérialisé
        """
        
        # Champs identiques pour toutes les langues
        data = {
            # Identifiants
            'id': program.id,
            'school_id': program.school_id,
            'slug': program.slug,
            'eef_name': program.eef_name,
            
            # Noms et descriptions (traduits)
            'title': cls.get_translated_field(program, 'name', locale),
            'name': cls.get_translated_field(program, 'name', locale),
            'description': cls.get_translated_field(program, 'description', locale),
            'desired_profiles': cls.get_translated_field(program, 'desired_profiles', locale),
            'curriculum_highlights': cls.get_translated_field(program, 'curriculum_highlights', locale),
            'special_comment': cls.get_translated_field(program, 'special_comment', locale),
            
            # Diplôme et niveau
            'grade': program.grade,
            'rncp_level': program.rncp_level,
            'rncp_certifier': program.rncp_certifier,

            # Durée et format
            'fi_school_duration': cls.get_translated_field(program, 'fi_school_duration', locale),
            'fi_duration_comment': cls.get_translated_field(program, 'fi_duration_comment', locale),
            'ca_school_duration': cls.get_translated_field(program, 'ca_school_duration', locale),
            'ca_program_details': cls.get_translated_field(program, 'ca_program_details', locale),
            #'alternance_possible': program.alternance_possible,
            
            # Coûts
            'tuition': cls.get_translated_field(program, 'tuition', locale),
            'tuition_comment': cls.get_translated_field(program, 'tuition_comment', locale),
            'first_deposit': cls.get_translated_field(program, 'first_deposit', locale),
            'first_deposit_comment': cls.get_translated_field(program, 'first_deposit_comment', locale),
            'fi_registration_fee': program.fi_registration_fee,
            'fi_annual_tuition_fee': program.fi_annual_tuition_fee,
            
            # Dates
            'intake': cls.get_translated_field(program, 'intake', locale),
            'intake_comment': cls.get_translated_field(program, 'intake_comment', locale),
            'application_date': cls.get_translated_field(program, 'application_date', locale),
            'application_date_comment': cls.get_translated_field(program, 'application_date_comment', locale),
            
            # Compétences et carrières (traduites)
            'skills_acquired': cls.get_translated_field(program, 'skills_acquired', locale),
            'careers': cls.get_translated_field(program, 'careers', locale),
            'corporate_partners': cls.get_translated_field(program, 'corporate_partners', locale),
            'employment_rate_among_graduates': cls.get_translated_field(program, 'employment_rate_among_graduates', locale),
            'success_rate_of_the_program': cls.get_translated_field(program, 'success_rate_of_the_program', locale),
            'starting_salary': cls.get_translated_field(program, 'starting_salary', locale),
            
            # Partenaires
            'partner_companies': cls.get_translated_field(program, 'partner_companies', locale),
            
            # Certifications
            'state_certification_type': cls.get_translated_field(program, 'state_certification_type', locale),
            'state_certification_type_complement': cls.get_translated_field(program, 'state_certification_type_complement', locale),
            'state_certification_type_complement2': cls.get_translated_field(program, 'state_certification_type_complement2', locale),
            'joint_preparation_with': cls.get_translated_field(program, 'joint_preparation_with', locale),
            'degree_issuer': cls.get_translated_field(program, 'degree_issuer', locale),
            'dual_degree_with': cls.get_translated_field(program, 'dual_degree_with', locale),
            'apprenticeship_manager': program.apprenticeship_manager,
        
            
            # Domaines et sous-domaines
            #'domain': program.domain,
            'sub_domain1': program.sub_domain1_id,
            'sub_domain2': program.sub_domain2_id,
            'sub_domain3': program.sub_domain3_id,

            # SEO
            'seo_title': cls.get_translated_field(program, 'seo_title', locale),
            'seo_description': cls.get_translated_field(program, 'seo_description', locale),
            'seo_keywords': cls.get_translated_field(program, 'seo_keywords', locale),

            # URL
            'url_application': program.url_application,

            # Métadonnées et Campus France
            'is_active': program.is_active,
            'parallel_procedure': program.parallel_procedure,
            'bienvenue_en_france_level': program.bienvenue_en_france_level,
            'contact': program.contact,
            'is_referenced_in_eef': program.is_referenced_in_eef,
            'address': program.address,
            'phone': program.phone,
            'email': program.email,
        }
        
        # Admission par année (si disponible)
        for i in range(1, 6):
            data[f'y{i}_required_level'] = cls.get_translated_field(program, f'y{i}_required_level', locale) if hasattr(program, f'y{i}_required_level') else None
            data[f'required_degree{i}'] = cls.get_translated_field(program, f'required_degree{i}', locale) if hasattr(program, f'required_degree{i}') else None
            data[f'y{i}_required_degree'] = cls.get_translated_field(program, f'y{i}_required_degree', locale) if hasattr(program, f'y{i}_required_degree') else None
            data[f'y{i}_admission_method'] = cls.get_translated_field(program, f'y{i}_admission_method', locale) if hasattr(program, f'y{i}_admission_method') else None
            data[f'y{i}_admission_details'] = cls.get_translated_field(program, f'y{i}_admission_details', locale) if hasattr(program, f'y{i}_admission_details') else None
            data[f'y{i}_application_date'] = cls.get_translated_field(program, f'y{i}_application_date', locale) if hasattr(program, f'y{i}_application_date') else None
            data[f'y{i}_teaching_language_with_required_level'] = cls.get_translated_field(program, f'y{i}_teaching_language_with_required_level', locale) if hasattr(program, f'y{i}_teaching_language_with_required_level') else None
            data[f'language_tech_level_unofficial{i}'] = cls.get_translated_field(program, f'language_tech_level_unofficial{i}', locale) if hasattr(program, f'language_tech_level_unofficial{i}') else None
            data[f'language_tech_level{i}'] = cls.get_translated_field(program, f'language_tech_level{i}', locale) if hasattr(program, f'language_tech_level{i}') else None
        # Inclure l'école si demandé
        if include_school and hasattr(program, 'school') and program.school:
            from .school_serializer import SchoolSerializer
            data['school'] = SchoolSerializer.serialize(program.school, locale)
        elif include_school:
            data['school_name'] = program.school_name
        
        return data
    
    @classmethod
    def serialize_many(cls, programs, locale='fr', include_school=False):
        """Sérialise une liste de programmes"""
        return [cls.serialize(program, locale, include_school) for program in programs]
