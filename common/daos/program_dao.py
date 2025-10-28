# common/daos/program_dao.py
from common.models.program import Program
from common.models.school import School
from sqlalchemy import or_, and_, Integer, func, distinct
from sqlalchemy.sql.sqltypes import Numeric
import re

class ProgramDAO:
    def __init__(self, model):
        self.model = model    

    def _extract_price_from_string(self, price_string):
        """
        Extrait le prix numérique d'une chaîne
        Gère les formats: "1000€", "1 000€", "1000", "1 000€ à 2 000€"
        """
        if not price_string:
            return None, None
            
        # Nettoyer la chaîne
        clean_string = str(price_string).replace('€', '').replace(' ', '').replace(',', '')
        
        # Chercher les nombres
        numbers = re.findall(r'\d+', clean_string)
        
        if not numbers:
            return None, None
            
        if 'à' in price_string or '-' in price_string:
            # Fourchette de prix
            if len(numbers) >= 2:
                return int(numbers[0]), int(numbers[1])
            else:
                # Si un seul nombre dans une fourchette, utiliser comme min
                return int(numbers[0]), None
        else:
            # Prix unique
            price = int(numbers[0])
            return price, price

    def _create_price_filter(self, field_name, min_val=None, max_val=None):
        """
        Crée un filtre SQL robuste pour les champs de prix
        """
        conditions = []
        
        if min_val is not None or max_val is not None:
            # Exclure les valeurs NULL ou vides
            base_condition = and_(
                field_name.isnot(None),
                field_name != '',
                field_name != 'Non spécifié',
                field_name != 'Nous consulter'
            )
            conditions.append(base_condition)
        
        if min_val is not None:
            # Condition pour prix minimum
            min_condition = or_(
                # Prix unique >= min_val
                and_(
                    ~field_name.like('%à%'),
                    ~field_name.like('%-%'),
                    func.cast(
                        func.regexp_replace(
                            func.regexp_replace(field_name, '[^0-9]', ''),
                            '^$', '0'
                        ), Integer
                    ) >= min_val
                ),
                # Fourchette: prix max >= min_val (chevauchement possible)
                and_(
                    or_(field_name.like('%à%'), field_name.like('%-%')),
                    func.cast(
                        func.regexp_replace(
                            func.substring_index(
                                func.regexp_replace(field_name, '[^0-9à-]', ''), 
                                'à', -1
                            ),
                            '[^0-9]', ''
                        ), Integer
                    ) >= min_val
                )
            )
            conditions.append(min_condition)
        
        if max_val is not None:
            # Condition pour prix maximum
            max_condition = or_(
                # Prix unique <= max_val
                and_(
                    ~field_name.like('%à%'),
                    ~field_name.like('%-%'),
                    func.cast(
                        func.regexp_replace(field_name, '[^0-9]', ''),
                        Integer
                    ) <= max_val
                ),
                # Fourchette: prix min <= max_val (chevauchement possible)
                and_(
                    or_(field_name.like('%à%'), field_name.like('%-%')),
                    func.cast(
                        func.regexp_replace(
                            func.substring_index(
                                func.regexp_replace(field_name, '[^0-9à-]', ''), 
                                'à', 1
                            ),
                            '[^0-9]', ''
                        ), Integer
                    ) <= max_val
                )
            )
            conditions.append(max_condition)
        
        return and_(*conditions) if conditions else None

    def get_all_programs(self):
        """Récupère tous les programmes actifs avec leurs écoles"""
        programs = self.model.query.filter_by(is_active=True).all()
        result = []
        for program in programs:
            program_data = program.as_dict()
            if program_data:  # Vérifie que le programme est actif
                # Ajouter les informations de l'école
                if program.school:
                    school_data = program.school.as_dict()
                    if school_data:  # Vérifie que l'école est publique
                        program_data['school'] = school_data
                        result.append(program_data)
        return result
    
    def get_program_by_id(self, program_id):
        """Récupère un programme par son ID"""
        program = self.model.query.filter_by(id=program_id, is_active=True).first()
        if program:
            program_data = program.as_dict_with_subdomains()
            if program.school:
                program_data['school'] = program.school.as_dict()
                return program_data
        return None
    
    def get_program_by_slug(self, slug):
        """Récupère un programme par son slug (retourne l'OBJET, pas un dict)"""
        program = self.model.query.filter_by(slug=slug, is_active=True).first()
        return program
    
    def get_program_by_slug_as_dict(self, slug):
        """Récupère un programme par son slug (version dict - pour compatibilité)"""
        program = self.model.query.filter_by(slug=slug, is_active=True).first()
        if program:
            program_data = program.as_dict_with_subdomains()
            if program.school:
                program_data['school'] = program.school.as_dict()
            return program_data
        return None    
    
    def get_programs_by_school_id(self, school_id):
        """Récupère tous les programmes d'une école"""
        programs = self.model.query.filter_by(school_id=school_id, is_active=True).all()
        result = []
        for program in programs:
            program_data = program.as_dict()
            if program_data and program.school:
                program_data['school'] = program.school.as_dict()
                result.append(program_data)
        return result
    
    def get_programs_by_school_slug(self, school_slug):
        """Récupère tous les programmes d'une école par son slug"""
        school = School.query.filter_by(slug=school_slug).first()
        if school:
            return self.get_programs_by_school_id(school.id)
        return []
    
    def get_all_program_slugs(self):
        """Récupère tous les slugs des programmes actifs"""
        programs = self.model.query.filter_by(is_active=True).with_entities(self.model.slug).all()
        return [program.slug for program in programs]
    
    def search_programs(self, filters=None):
        """Recherche de programmes avec filtres"""
        query = self.model.query.filter_by(is_active=True)
        
        if filters:
            # Filtre par texte de recherche
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        self.model.name.ilike(search_term),
                        self.model.description.ilike(search_term),
                        self.model.skills_acquired.ilike(search_term),
                        self.model.careers.ilike(search_term),
                        self.model.school_name.ilike(search_term)
                    )
                )
            
            # Filtre par école
            if filters.get('school_id'):
                query = query.filter_by(school_id=filters['school_id'])
            
            # Filtre par grade
            if filters.get('grade'):
                query = query.filter_by(grade=filters['grade'])
            
            # Filtre par durée
            if filters.get('duration'):
                query = query.filter_by(fi_school_duration=filters['duration'])
            
            # Filtre par alternance
            if filters.get('alternance') is not None:
                query = query.filter_by(alternance_possible=filters['alternance'])

            # ✅ FILTRES DE PRIX - FRAIS DE SCOLARITÉ - MANQUAIENT
            if filters.get('tuition_min') or filters.get('tuition_max'):
                try:
                    tuition_min = int(filters['tuition_min']) if filters.get('tuition_min') else None
                    tuition_max = int(filters['tuition_max']) if filters.get('tuition_max') else None
                    
                    print(f"🔍 Applying tuition filters: min={tuition_min}, max={tuition_max}")
                    
                    price_filter = self._create_price_filter(
                        self.model.tuition, 
                        tuition_min, 
                        tuition_max
                    )
                    
                    if price_filter is not None:
                        query = query.filter(price_filter)
                        print(f"✅ Tuition filter applied successfully")
                    
                except (ValueError, TypeError) as e:
                    print(f"❌ Erreur dans les filtres de scolarité: {e}")

            # ✅ FILTRES D'ACOMPTE CORRIGÉS
            if filters.get('deposit_min') or filters.get('deposit_max'):
                try:
                    deposit_min = int(filters['deposit_min']) if filters.get('deposit_min') else None
                    deposit_max = int(filters['deposit_max']) if filters.get('deposit_max') else None
                    
                    print(f"🔍 Applying deposit filters: min={deposit_min}, max={deposit_max}")
                    
                    # Utiliser le bon nom de colonne : first_deposit
                    deposit_filter = self._create_price_filter(
                        self.model.first_deposit, 
                        deposit_min, 
                        deposit_max
                    )
                    
                    if deposit_filter is not None:
                        query = query.filter(deposit_filter)
                        print(f"✅ Deposit filter applied successfully")
                    
                except (ValueError, TypeError) as e:
                    print(f"❌ Erreur dans les filtres d'acompte: {e}")

            # Filtre par sous-domaines
            if filters.get('subdomain_ids'):
                subdomain_conditions = []
                for subdomain_id in filters['subdomain_ids']:
                    subdomain_conditions.append(self.model.sub_domain1_id == subdomain_id)
                    subdomain_conditions.append(self.model.sub_domain2_id == subdomain_id)
                    subdomain_conditions.append(self.model.sub_domain3_id == subdomain_id)
                query = query.filter(or_(*subdomain_conditions))
        
        programs = query.all()
        result = []
        for program in programs:
            program_data = program.as_dict_with_subdomains()
            if program.school:
                program_data['school'] = program.school.as_dict()
                result.append(program_data)
        return result
    
    def get_similar_programs(self, program_id, limit=3):
        """Récupère les programmes similaires basés sur les sous-domaines"""
        current_program = self.model.query.filter_by(id=program_id, is_active=True).first()
        if not current_program:
            return []
        
        # Récupérer les sous-domaines du programme courant
        current_subdomains = [
            current_program.sub_domain1_id,
            current_program.sub_domain2_id, 
            current_program.sub_domain3_id
        ]
        current_subdomains = [sd for sd in current_subdomains if sd]
        
        if not current_subdomains:
            return []
        
        # Rechercher les programmes avec des sous-domaines communs
        similar_conditions = []
        for subdomain_id in current_subdomains:
            similar_conditions.append(self.model.sub_domain1_id == subdomain_id)
            similar_conditions.append(self.model.sub_domain2_id == subdomain_id)
            similar_conditions.append(self.model.sub_domain3_id == subdomain_id)
        
        similar_programs = (self.model.query
                          .filter(and_(
                              self.model.id != program_id,
                              self.model.grade == current_program.grade,
                              self.model.is_active == True,
                              or_(*similar_conditions)
                          ))
                          .limit(limit * 2)  # Récupérer plus pour filtrer ensuite
                          .all())
        
        # Calculer la similarité et trier
        program_scores = []
        for program in similar_programs:
            program_subdomains = [
                program.sub_domain1_id,
                program.sub_domain2_id,
                program.sub_domain3_id
            ]
            program_subdomains = [sd for sd in program_subdomains if sd]
            
            # Calculer le score de similarité
            common_subdomains = set(current_subdomains) & set(program_subdomains)
            similarity_score = len(common_subdomains)
            
            # Bonus si même école
            if program.school_id == current_program.school_id:
                similarity_score += 1
            
            # Bonus si même type de certification d'état
            if program.state_certification_type_complement == current_program.state_certification_type_complement:
                similarity_score += 0.5
            
            program_scores.append((program, similarity_score))
        
        # Trier par score et retourner les meilleurs
        program_scores.sort(key=lambda x: x[1], reverse=True)
        result = []
        for program, score in program_scores[:limit]:
            if program.school:
                program_data = program.as_dict_with_subdomains()
                program_data['school'] = program.school.as_dict()
                program_data['similarity_score'] = score
                result.append(program_data)
        
        return result
    
    # common/daos/program_dao.py
    def search_programs_paginated(self, filters=None, page=1, limit=12, locale='fr'):
        """Recherche de programmes avec pagination et support i18n"""
        print(f"🔍 search_programs_paginated locale={locale}, filters={filters}")
        
        query = (self.model.query
                .join(School, self.model.school_id == School.id)
                .filter(
                    self.model.is_active == True,
                    School.is_public == False
                ))
        
        # ✅ IMPORTANT : En mode EN, filtrer programmes avec traduction
        if locale == 'en':
            print("🌍 Filtering ONLY programs with English translation")
            query = query.filter(
                self.model.name_en.isnot(None),
                self.model.name_en != ''
            )
        
        total_without_filters = query.count()
        print(f"🔍 Programs before filters: {total_without_filters}")
        
        if filters:
            # RECHERCHE TEXTUELLE
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                if locale == 'en':
                    query = query.filter(
                        or_(
                            self.model.name_en.ilike(search_term),
                            self.model.description_en.ilike(search_term),
                            self.model.skills_acquired_en.ilike(search_term),
                            self.model.careers_en.ilike(search_term),
                            self.model.school_name.ilike(search_term)
                        )
                    )
                else:
                    query = query.filter(
                        or_(
                            self.model.name.ilike(search_term),
                            self.model.description.ilike(search_term),
                            self.model.skills_acquired.ilike(search_term),
                            self.model.careers.ilike(search_term),
                            self.model.school_name.ilike(search_term)
                        )
                    )

            # CAMPUS FRANCE
            if filters.get('campus_france_connected'):
                query = query.filter(School.connection_campus_france == True)
            if filters.get('parallel_procedure'):
                query = query.filter(self.model.parallel_procedure == True)
            if filters.get('exoneration') is not None:
                query = query.filter(School.exoneration_tuition == int(filters['exoneration']))
            if filters.get('bienvenue_france_level'):
                query = query.filter(
                    self.model.bienvenue_en_france_level == int(filters['bienvenue_france_level'])
                )

            # NIVEAU ENTRÉE
            if filters.get('entry_level'):
                entry_level = filters['entry_level']
                level_conditions = []
                for year in range(1, 6):
                    level_field = getattr(self.model, f'y{year}_required_level', None)
                    if level_field:
                        level_conditions.append(level_field.ilike(f'%{entry_level}%'))
                if level_conditions:
                    query = query.filter(or_(*level_conditions))

            # GRADE
            if filters.get('grade'):
                if locale == 'en':
                    query = query.filter(
                        or_(
                            self.model.state_certification_type_en == filters['grade'],
                            self.model.state_certification_type_complement_en == filters['grade']
                        )
                    )
                else:
                    query = query.filter(
                        or_(
                            self.model.grade == filters['grade'],
                            self.model.state_certification_type == filters['grade'],
                            self.model.state_certification_type_complement == filters['grade']
                        )
                    )

            # DURÉES
            if filters.get('durations'):
                query = query.filter(self.model.fi_school_duration.in_(filters['durations']))

            # ALTERNANCE
            print("Filtering by alternance🇩🇿🇩🇿", filters.get('alternance'))
            if filters.get('alternance') is not None:
                has_alternance = str(filters['alternance']).lower() == 'true'
                if has_alternance:
                    query = query.filter(
                        and_(
                            self.model.ca_school_duration.isnot(None),
                            self.model.ca_school_duration != '',
                            func.trim(self.model.ca_school_duration) != ''  # Exclut les espaces
                        )
                    )
                else:
                    query = query.filter(
                        or_(
                            self.model.ca_school_duration.is_(None),
                            self.model.ca_school_duration == '',
                            func.trim(self.model.ca_school_duration) == ''
                        )
                    )

            # SOUS-DOMAINES
            if filters.get('subdomain_ids'):
                subdomain_conditions = []
                for sid in filters['subdomain_ids']:
                    subdomain_conditions.extend([
                        self.model.sub_domain1_id == sid,
                        self.model.sub_domain2_id == sid,
                        self.model.sub_domain3_id == sid
                    ])
                if subdomain_conditions:
                    query = query.filter(or_(*subdomain_conditions))

            # VILLE
            if filters.get('city'):
                query = query.filter(School.base_city == filters['city'])

            # LANGUE
            if filters.get('language'):
                language = filters['language']
                language_conditions = []
                for year in range(1, 6):
                    primary = getattr(self.model, f'language_tech_level{year}', None)
                    unofficial = getattr(self.model, f'language_tech_level_unofficial{year}', None)
                    if primary and unofficial:
                        language_conditions.append(
                            func.coalesce(func.nullif(primary, ''), unofficial).ilike(f'%{language}%')
                        )
                    elif primary:
                        language_conditions.append(primary.ilike(f'%{language}%'))
                    elif unofficial:
                        language_conditions.append(unofficial.ilike(f'%{language}%'))
                if language_conditions:
                    query = query.filter(or_(*language_conditions))

            # FRAIS SCOLARITÉ
            if filters.get('tuition_min') or filters.get('tuition_max'):
                tuition_min = int(filters.get('tuition_min', 0))
                tuition_max = int(filters.get('tuition_max', 999999))
                price_filter = self._create_price_filter(self.model.tuition, tuition_min, tuition_max)
                if price_filter is not None:
                    query = query.filter(price_filter)

            # ACOMPTE
            if filters.get('deposit_min') or filters.get('deposit_max'):
                deposit_min = int(filters.get('deposit_min', 0))
                deposit_max = int(filters.get('deposit_max', 999999))
                deposit_filter = self._create_price_filter(self.model.first_deposit, deposit_min, deposit_max)
                if deposit_filter is not None:
                    query = query.filter(deposit_filter)

            # RNCP
            if filters.get('rncp_level'):
                query = query.filter(self.model.rncp_level == filters['rncp_level'])

            # DATE CANDIDATURE
            if filters.get('application_date'):
                query = query.filter(self.model.application_date.ilike(f"%{filters['application_date']}%"))

            # ÉCOLE
            if filters.get('school_id'):
                query = query.filter(self.model.school_id == filters['school_id'])

        total_count = query.count()
        print(f"🔍 Total after filters: {total_count}")
        
        offset = (page - 1) * limit
        programs = query.offset(offset).limit(limit).all()
        
        # ✅ LOCALISER TOUS LES CHAMPS
        result = []
        for program in programs:
            try:
                program_data = {}
                
                if locale == 'en':
                    # ✅ CHAMPS PROGRAMME EN ANGLAIS
                    program_data = {
                                # Identifiants
                                'id': program.id,
                                'school_id': program.school_id,
                                'school_name': program.school_name,
                                'eef_name': program.eef_name,
                                'slug': program.slug,
                                
                                # Noms et descriptions
                                'title': program.name_en or program.name,
                                'name': program.name_en or program.name,
                                'description': program.description_en or program.description,
                                'desired_profiles': program.desired_profiles_en or program.desired_profiles,
                                'curriculum_highlights': program.curriculum_highlights_en or program.curriculum_highlights,
                                'skills_acquired': program.skills_acquired_en or program.skills_acquired,
                                'special_comment': program.special_comment_en or program.special_comment,
                                
                                # Durée et organisation
                                'fi_school_duration': program.fi_school_duration_en or program.fi_school_duration,
                                'fi_duration_comment': program.fi_duration_comment_en or program.fi_duration_comment,
                                'ca_school_duration': program.ca_school_duration_en or program.ca_school_duration,
                                'ca_program_details': program.ca_program_details_en or program.ca_program_details,
                                
                                # Candidatures et admissions
                                'application_date': program.application_date_en or program.application_date,
                                'application_date_comment': program.application_date_comment_en or program.application_date_comment,
                                'intake': program.intake_en or program.intake,
                                'intake_comment': program.intake_comment_en or program.intake_comment,
                                'intake_capacity': program.intake_capacity,
                                'url_application': program.url_application,
                                
                                # Domaines
                                'sub_domain1_id': program.sub_domain1_id,
                                'sub_domain2_id': program.sub_domain2_id,
                                'sub_domain3_id': program.sub_domain3_id,
                                
                                # Certifications et grade
                                'state_certification_type': program.state_certification_type_en or program.state_certification_type,
                                'state_certification_type_complement': program.state_certification_type_complement_en or program.state_certification_type_complement,
                                'state_certification_type_complement2': program.state_certification_type_complement2_en or program.state_certification_type_complement2,
                                'rncp_level': program.rncp_level,
                                'rncp_certifier': program.rncp_certifier,
                                'grade': program.grade,
                                
                                # Partenariats
                                'joint_preparation_with': program.joint_preparation_with_en or program.joint_preparation_with,
                                'degree_issuer': program.degree_issuer_en or program.degree_issuer,
                                'dual_degree_with': program.dual_degree_with_en or program.dual_degree_with,
                                'international_double_degree': program.international_double_degree_en or program.international_double_degree,
                                'apprenticeship_manager': program.apprenticeship_manager,
                                
                                # Frais de scolarité
                                'fi_registration_fee': program.fi_registration_fee,
                                'fi_annual_tuition_fee': program.fi_annual_tuition_fee,
                                'tuition_comment': program.tuition_comment_en or program.tuition_comment,
                                'tuition': program.tuition_en or program.tuition,
                                'y1_tuition': program.y1_tuition,
                                'y2_tuition': program.y2_tuition,
                                'y3_tuition': program.y3_tuition,
                                'y4_tuition': program.y4_tuition,
                                'y5_tuition': program.y5_tuition,
                                'first_deposit_comment': program.first_deposit_comment_en or program.first_deposit_comment,
                                'first_deposit': program.first_deposit_en or program.first_deposit,
                                
                                # Admissions Année 1
                                'y1_required_level': program.y1_required_level,
                                'required_degree1': program.required_degree1,
                                'y1_admission_details': program.y1_admission_details_en or program.y1_admission_details,
                                'y1_teaching_language_with_required_level': program.y1_teaching_language_with_required_level,
                                'language_tech_level1': program.language_tech_level1_en or program.language_tech_level1,
                                
                                # Admissions Année 2
                                'y2_required_level': program.y2_required_level,
                                'required_degree2': program.required_degree2,
                                'y2_admission_details': program.y2_admission_details_en or program.y2_admission_details,
                                'y2_admission_method': program.y2_admission_method_en or program.y2_admission_method,
                                'y2_application_date': program.y2_application_date_en or program.y2_application_date,
                                'y2_teaching_language_with_required_level': program.y2_teaching_language_with_required_level,
                                'language_tech_level2': program.language_tech_level2_en or program.language_tech_level2,
                                
                                # Admissions Année 3
                                'y3_required_level': program.y3_required_level_en or program.y3_required_level,
                                'required_degree3': program.required_degree3,
                                'y3_required_degree': program.y3_required_degree_en or program.y3_required_degree,
                                'y3_admission_method': program.y3_admission_method_en or program.y3_admission_method,
                                'y3_admission_details': program.y3_admission_details_en or program.y3_admission_details,
                                'y3_application_date': program.y3_application_date_en or program.y3_application_date,
                                'y3_teaching_language_with_required_level': program.y3_teaching_language_with_required_level,
                                'language_tech_level3': program.language_tech_level3_en or program.language_tech_level3,
                                'y3_admission_by_exam': program.y3_admission_by_exam_en or program.y3_admission_by_exam,
                                
                                # Admissions Année 4
                                'y4_required_level': program.y4_required_level_en or program.y4_required_level,
                                'required_degree4': program.required_degree4,
                                'y4_admission_method': program.y4_admission_method_en or program.y4_admission_method,
                                'y4_admission_details': program.y4_admission_details_en or program.y4_admission_details,
                                'y4_application_date': program.y4_application_date_en or program.y4_application_date,
                                'y4_teaching_language_with_required_level': program.y4_teaching_language_with_required_level,
                                'language_tech_level4': program.language_tech_level4_en or program.language_tech_level4,
                                
                                # Admissions Année 5
                                'y5_required_level': program.y5_required_level_en or program.y5_required_level,
                                'required_degree5': program.required_degree5,
                                'y5_admission_method': program.y5_admission_method_en or program.y5_admission_method,
                                'y5_application_date': program.y5_application_date_en or program.y5_application_date,
                                'y5_admission_details': program.y5_admission_details_en or program.y5_admission_details,
                                'y5_teaching_language_with_required_level': program.y5_teaching_language_with_required_level_en or program.y5_teaching_language_with_required_level,
                                'language_tech_level5': program.language_tech_level5_en or program.language_tech_level5,
                                
                                # SEO
                                'seo_title': program.seo_title_en or program.seo_title,
                                'seo_description': program.seo_description_en or program.seo_description,
                                'seo_keywords': program.seo_keywords_en or program.seo_keywords,
                                
                                # Carrières et statistiques
                                'careers': program.careers_en or program.careers,
                                'corporate_partners': program.corporate_partners,
                                'employment_rate_among_graduates': program.employment_rate_among_graduates_en or program.employment_rate_among_graduates,
                                'success_rate_of_the_program': program.success_rate_of_the_program_en or program.success_rate_of_the_program,
                                'starting_salary': program.starting_salary_en or program.starting_salary,
                                
                                # Langues non officielles
                                'language_tech_level_unofficial1': program.language_tech_level_unofficial1_en or program.language_tech_level_unofficial1,
                                'language_tech_level_unofficial2': program.language_tech_level_unofficial2_en or program.language_tech_level_unofficial2,
                                'language_tech_level_unofficial3': program.language_tech_level_unofficial3_en or program.language_tech_level_unofficial3,
                                'language_tech_level_unofficial4': program.language_tech_level_unofficial4_en or program.language_tech_level_unofficial4,
                                'language_tech_level_unofficial5': program.language_tech_level_unofficial5_en or program.language_tech_level_unofficial5,
                                
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
                else:
                    # ✅ CHAMPS PROGRAMME EN FRANÇAIS
                    program_data = program.as_dict_with_subdomains()
                    program_data['title'] = program.name
                
                # ✅ LOCALISER SCHOOL
                if program.school:
                # ✅ SCHOOL EN ANGLAIS - VERSION COMPLÈTE
                    school_dict = {
                        # Identifiants
                        'id': program.school.id,
                        'slug': program.school.slug,
                        'school_group': program.school.school_group,
                        'base_city': program.school.base_city,
                        
                        # Coordonnées
                        'address': program.school.address,
                        'phone': program.school.phone,
                        'email': program.school.email,
                        'name': program.school.name,
                        'description': program.school.description_en or program.school.description,
                        
                        # Frais et exonérations
                        'exoneration_tuition': program.school.exoneration_tuition,
                        'exoneration_tuition_comment': program.school.exoneration_tuition_comment_en or program.school.exoneration_tuition_comment,
                        
                        # Statut
                        'hors_contrat': program.school.hors_contrat,
                        'acknowledgement': program.school.acknowledgement,
                        
                        # Alternance
                        'alternance_rate': program.school.alternance_rate,
                        'alternance_comment': program.school.alternance_comment,
                        'alternance_comment_tech': program.school.alternance_comment_tech_en or program.school.alternance_comment_tech,
                        'work_study_programs': program.school.work_study_programs_en or program.school.work_study_programs,
                        
                        # Étudiants internationaux
                        'international_student_rate': program.school.international_student_rate,
                        'international_student_rate_tech': program.school.international_student_rate_tech,
                        'international_student_comment': program.school.international_student_comment_en or program.school.international_student_comment,
                        'international_student_comment_tech': program.school.international_student_comment_tech,
                        
                        # Campus France
                        'connection_campus_france': program.school.connection_campus_france,
                        
                        # Évaluations
                        'rating': str(program.school.rating) if program.school.rating else None,
                        'reviews_counter': program.school.reviews_counter,
                        
                        # URLs et réseaux sociaux
                        'url': program.school.url,
                        'facebook_url': program.school.facebook_url,
                        'x_url': program.school.x_url,
                        'linkedin_url': program.school.linkedin_url,
                        'instagram_url': program.school.instagram_url,
                        
                        # Rankings
                        'national_ranking': program.school.national_ranking_en or program.school.national_ranking,
                        'international_ranking': program.school.international_ranking_en or program.school.international_ranking,
                        
                        # Support international
                        'international_support_before_coming': program.school.international_support_before_coming_en or program.school.international_support_before_coming,
                        'international_support_after_coming': program.school.international_support_after_coming_en or program.school.international_support_after_coming,
                        
                        # Admission et partenariats
                        'general_entry_requirements': program.school.general_entry_requirements_en or program.school.general_entry_requirements,
                        'partnerships': program.school.partnerships_en or program.school.partnerships,
                        'facilities': program.school.facilities_en or program.school.facilities,
                        
                        # Visibilité
                        'is_public': program.school.is_public,
                        
                        # SEO
                        'seo_title': program.school.seo_title_en or program.school.seo_title,
                        'seo_description': program.school.seo_description_en or program.school.seo_description,
                        'seo_keywords': program.school.seo_keywords_en or program.school.seo_keywords,
                        
                        # Médias
                        'logo_path': program.school.logo_path,
                        'cover_page_path': program.school.cover_page_path,
                    }
                    
                    program_data['school'] = school_dict
                
                result.append(program_data)
                
            except Exception as e:
                print(f"❌ Error processing program {program.id}: {e}")
        
        print(f"✅ Returning {len(result)} localized programs")
        
        return {
            'data': result,
            'total': total_count,
            'page': page,
            'limit': limit,
            'pages': (total_count + limit - 1) // limit,
            'success': True
        }

    def get_programs_count(self):
        """Récupère le nombre total de programmes actifs"""
        return self.model.query.filter_by(is_active=True).count()

    def get_filter_options(self):
        """Récupère toutes les options de filtres disponibles avec déduplication"""
        print('🚨 Starting get_filter_options')
        
        try:
            # Base query pour les programmes actifs des écoles privées
            base_query = (self.model.query
                        .join(School, self.model.school_id == School.id)
                        .filter(
                            self.model.is_active == True,
                            School.is_public == False
                        ))
            
            print('✅ Base query created')
            
            # Récupérer tous les programmes pour analyser
            all_programs = base_query.all()
            print(f'✅ Found {len(all_programs)} programs')
            
            # 1. GRADES - Combinaison de 3 champs avec déduplication
            grade_set = set()
            for program in all_programs:
                if program.grade:
                    grade_set.add(program.grade.strip())
                if program.state_certification_type:
                    grade_set.add(program.state_certification_type.strip())
                if program.state_certification_type_complement:
                    grade_set.add(program.state_certification_type_complement.strip())
            
            print(f'✅ Processed {len(grade_set)} unique grades')
            
            # 2. DURÉES
            durations = base_query.with_entities(
                distinct(self.model.fi_school_duration)
            ).filter(
                self.model.fi_school_duration.isnot(None)
            ).all()
            
            print(f'✅ Processed {len(durations)} durations')
            
            # 3. DATES DE CANDIDATURE
            application_dates = base_query.with_entities(
                distinct(self.model.application_date)
            ).filter(
                self.model.application_date.isnot(None)
            ).all()
            
            print(f'✅ Processed {len(application_dates)} application dates')
            
            # 4. VILLES
            cities = base_query.with_entities(
                distinct(School.base_city)
            ).filter(
                School.base_city.isnot(None)
            ).all()
            
            print(f'✅ Processed {len(cities)} cities')
            
            # 5. NIVEAUX RNCP
            rncp_levels = base_query.with_entities(
                distinct(self.model.rncp_level)
            ).filter(
                self.model.rncp_level.isnot(None)
            ).all()
            
            print(f'✅ Processed {len(rncp_levels)} RNCP levels')
            
            # 6. NIVEAUX D'ENTRÉE - CORRECTION pour éliminer doublons
            entry_levels = set()
            for program in all_programs:
                for year in range(1, 6):
                    level_field = getattr(program, f'y{year}_required_level', None)
                    if level_field:
                        # ✅ Normaliser et dédupliquer
                        normalized_level = level_field.strip().title()  # "bac" -> "Bac"
                        
                        # ✅ Normaliser les espaces en fin ("Bac+4 " -> "Bac+4")
                        normalized_level = normalized_level.rstrip()
                        
                        # ✅ Standardiser les formats
                        if normalized_level.lower().startswith('bac'):
                            if '+' in normalized_level:
                                # "bac+2" -> "Bac+2"
                                parts = normalized_level.split('+')
                                if len(parts) == 2:
                                    normalized_level = f"Bac+{parts[1].strip()}"
                            else:
                                # "bac" -> "Bac"
                                normalized_level = "Bac"
                        
                        entry_levels.add(normalized_level)
            
            print(f'✅ Processed {len(entry_levels)} unique entry levels')
            
            # 7. LANGUES - CORRECTION pour éliminer doublons
            languages = set()
            for program in all_programs:
                for year in range(1, 6):
                    lang_field = getattr(program, f'language_tech_level{year}', None)
                    if lang_field:
                        try:
                            # Séparer les langues multiples (ex: "Fr-B2,En-C1")
                            lang_parts = str(lang_field).split(',')
                            for part in lang_parts:
                                part_clean = part.strip()
                                if part_clean:
                                    # ✅ Normaliser le format des langues
                                    if '-' in part_clean:
                                        lang, level = part_clean.split('-', 1)
                                        lang = lang.strip().title()  # "fr" -> "Fr"
                                        level = level.strip().upper()  # "b2" -> "B2"
                                        normalized_lang = f"{lang}-{level}"
                                        languages.add(normalized_lang)
                                    else:
                                        languages.add(part_clean)
                        except Exception as e:
                            print(f'Warning: Error processing language {lang_field}: {e}')
            
            print(f'✅ Processed {len(languages)} unique languages')
            
            # ✅ ORDRE LOGIQUE pour les niveaux d'entrée
            entry_levels_ordered = []
            level_order = ['Bac', 'Bac+1', 'Bac+2', 'Bac+3', 'Bac+4', 'Bac+5']
            
            # Ajouter d'abord les niveaux dans l'ordre logique
            for level in level_order:
                if level in entry_levels:
                    entry_levels_ordered.append(level)
                    entry_levels.remove(level)
            
            # Ajouter les niveaux restants (cas particuliers)
            entry_levels_ordered.extend(sorted(list(entry_levels)))
            
            # Construire le résultat final
            result = {
                'grades': sorted(list(grade_set)),
                'durations': sorted([d[0] for d in durations if d[0]]),
                'application_dates': sorted([d[0] for d in application_dates if d[0]]),
                'cities': sorted([c[0] for c in cities if c[0]]),
                'rncp_levels': sorted([str(r[0]) for r in rncp_levels if r[0]]),
                'entry_levels': entry_levels_ordered,  # ✅ Utiliser la liste ordonnée
                'languages': sorted(list(languages))
            }
            
            print('✅ Filter options built successfully')
            print(f'Entry levels: {result["entry_levels"]}')  # Debug
            
            return result
            
        except Exception as e:
            print(f'❌ Error in get_filter_options: {str(e)}')
            import traceback
            traceback.print_exc()
            
            # Retourner des options par défaut en cas d'erreur
            return {
                'grades': ['Licence', 'Master', 'Bachelor'],
                'durations': ['1 an', '2 ans', '3 ans'],
                'application_dates': ['Toute l\'année'],
                'cities': ['Paris', 'Lyon', 'Marseille'],
                'rncp_levels': ['6', '7'],
                'entry_levels': ['Bac', 'Bac+1', 'Bac+2', 'Bac+3', 'Bac+4', 'Bac+5'],  # ✅ Pas de doublons
                'languages': ['Fr-B2', 'En-B2']
            }
program_dao = ProgramDAO(Program)
