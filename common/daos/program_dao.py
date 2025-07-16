# common/daos/program_dao.py
from common.models.program import Program
from common.models.school import School
from sqlalchemy import or_, and_, Integer, func, distinct

class ProgramDAO:
    def __init__(self, model):
        self.model = model    
    
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
        """Récupère un programme par son slug"""
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
                print(f"🔍 Applying tuition filters: min={filters.get('tuition_min')}, max={filters.get('tuition_max')}")
                try:
                    if filters.get('tuition_min'):
                        min_val = int(filters['tuition_min'])
                        # Utiliser une approche plus simple pour MySQL
                        query = query.filter(
                            func.cast(
                                func.replace(
                                    func.replace(self.model.tuition, '€', ''),
                                    ' ', ''
                                ).op('REGEXP')('[0-9]+'),
                                'UNSIGNED'
                            ) >= min_val
                        )
                    
                    if filters.get('tuition_max'):
                        max_val = int(filters['tuition_max'])
                        query = query.filter(
                            func.cast(
                                func.replace(
                                    func.replace(self.model.tuition, '€', ''),
                                    ' ', ''
                                ).op('REGEXP')('[0-9]+'),
                                'UNSIGNED'
                            ) <= max_val
                        )
                except (ValueError, TypeError) as e:
                    print(f"Erreur dans les filtres de prix: {e}")
                    pass
            
            # ✅ FILTRES D'ACOMPTE - MANQUAIENT
            if filters.get('deposit_min') or filters.get('deposit_max'):
                print(f"🔍 Applying deposit filters: min={filters.get('deposit_min')}, max={filters.get('deposit_max')}")
                try:
                    if filters.get('deposit_min'):
                        min_val = int(filters['deposit_min'])
                        query = query.filter(
                            func.cast(
                                func.replace(
                                    func.replace(self.model.first_deposit, '€', ''),
                                    ' ', ''
                                ).op('REGEXP')('[0-9]+'),
                                'UNSIGNED'
                            ) >= min_val
                        )
                    
                    if filters.get('deposit_max'):
                        max_val = int(filters['deposit_max'])
                        query = query.filter(
                            func.cast(
                                func.replace(
                                    func.replace(self.model.first_deposit, '€', ''),
                                    ' ', ''
                                ).op('REGEXP')('[0-9]+'),
                                'UNSIGNED'
                            ) <= max_val
                        )
                except (ValueError, TypeError) as e:
                    print(f"Erreur dans les filtres d'acompte: {e}")
                    pass

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
            
            # Bonus si même grade
            if program.grade == current_program.grade:
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
    
    def search_programs_paginated(self, filters=None, page=1, limit=12):
        """Recherche de programmes avec pagination côté serveur"""
        print(f"🔍 search_programs_paginated called with filters: {filters}")
        
        # ✅ Base query : programmes actifs dans écoles privées
        query = (self.model.query
                .join(School, self.model.school_id == School.id)
                .filter(
                    self.model.is_active == True,
                    School.is_public == False
                ))
        
        print(f"🔍 Base query created")
        
        # ✅ Compter AVANT les filtres pour debug
        total_without_filters = query.count()
        print(f"🔍 Total programs before filters: {total_without_filters}")
        
        if filters:
            print(f"🔍 Applying filters: {list(filters.keys())}")
            
            # Filtre par texte de recherche
            if filters.get('search'):
                print(f"🔍 Applying search filter: {filters['search']}")
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

            # Filtre par niveau d'entrée
            if filters.get('entry_level'):
                print(f"🔍 Applying entry_level filter: {filters['entry_level']}")
                entry_level = filters['entry_level']
                level_conditions = []
                for year in range(1, 6):
                    level_field = getattr(self.model, f'y{year}_required_level', None)
                    if level_field:
                        level_conditions.append(level_field.ilike(f'%{entry_level}%'))
                if level_conditions:
                    query = query.filter(or_(*level_conditions))       

            # Filtre par grade
            if filters.get('grade'):
                print(f"🔍 Applying grade filter: {filters['grade']}")
                grade_value = filters['grade']
                query = query.filter(
                    or_(
                        self.model.grade == grade_value,
                        self.model.state_certification_type == grade_value,
                        self.model.state_certification_type_complement == grade_value
                    )
                )
            
            # Filtre par durée
            if filters.get('duration'):
                print(f"🔍 Applying duration filter: {filters['duration']}")
                query = query.filter(self.model.fi_school_duration == filters['duration'])
            
            # Filtre par alternance
            if filters.get('alternance') is not None:
                print(f"🔍 Applying alternance filter: {filters['alternance']}")
                if isinstance(filters['alternance'], bool):
                    has_alternance = filters['alternance']
                else:
                    has_alternance = str(filters['alternance']).lower() == 'true'
                
                if has_alternance:
                    query = query.filter(self.model.ca_school_duration.isnot(None))
                else:
                    query = query.filter(self.model.ca_school_duration.is_(None))
            
            # Filtre par sous-domaines - SEULEMENT si fourni
            if filters.get('subdomain_ids') and len(filters['subdomain_ids']) > 0:
                print(f"🔍 Applying subdomain filter: {filters['subdomain_ids']}")
                subdomain_conditions = []
                for subdomain_id in filters['subdomain_ids']:
                    subdomain_conditions.append(self.model.sub_domain1_id == subdomain_id)
                    subdomain_conditions.append(self.model.sub_domain2_id == subdomain_id)
                    subdomain_conditions.append(self.model.sub_domain3_id == subdomain_id)
                if subdomain_conditions:
                    query = query.filter(or_(*subdomain_conditions))
            
            # Filtre par ville
            if filters.get('city'):
                print(f"🔍 Applying city filter: {filters['city']}")
                query = query.filter(School.base_city == filters['city'])

            # Filtre langue d'enseignement
            if filters.get('language'):
                print(f"🔍 Applying language filter: {filters['language']}")
                language = filters['language']
                language_conditions = []
                for year in range(1, 6):
                    lang_field = getattr(self.model, f'language_tech_level{year}', None)
                    if lang_field:
                        language_conditions.append(lang_field.ilike(f'%{language}%'))
                if language_conditions:
                    query = query.filter(or_(*language_conditions)) 

            if filters.get('tuition_min') or filters.get('tuition_max'):
                print(f"🔍 Applying tuition filters: min={filters.get('tuition_min')}, max={filters.get('tuition_max')}")
                
                try:
                    if filters.get('tuition_min'):
                        min_val = int(filters['tuition_min'])
                        print(f"🔍 Filtering tuition >= {min_val}")
                        
                        # ✅ Version simplifiée : chercher dans le champ directement
                        # Pour "5 500 €" ou "5 900€ à 7 900€", on extrait le premier nombre
                        query = query.filter(
                            # Utiliser REGEXP pour extraire le premier nombre
                            func.cast(
                                func.regexp_substr(self.model.tuition, '[0-9 ]+'),  # Extrait "5 500" de "5 500 €"
                                'UNSIGNED'
                            ) >= min_val
                        )
                    
                    if filters.get('tuition_max'):
                        max_val = int(filters['tuition_max'])
                        print(f"🔍 Filtering tuition <= {max_val}")
                        
                        # Pour le max, on prend aussi le premier nombre (car "5 900€ à 7 900€" → on filtre sur 5900)
                        query = query.filter(
                            func.cast(
                                func.regexp_substr(self.model.tuition, '[0-9 ]+'),
                                'UNSIGNED'
                            ) <= max_val
                        )
                        
                except Exception as e:
                    print(f"❌ Erreur dans les filtres de prix: {e}")
                    # ✅ Version de fallback plus simple
                    try:
                        if filters.get('tuition_min'):
                            min_val = str(filters['tuition_min'])
                            # Recherche simple dans le texte
                            query = query.filter(self.model.tuition.like(f'%{min_val}%'))
                            print(f"🔍 Fallback: searching for '{min_val}' in tuition field")
                    except:
                        print("❌ Even fallback failed for tuition filters")
                        pass
            
            # ✅ CORRECTION FILTRES ACOMPTE - Version simplifiée
            if filters.get('deposit_min') or filters.get('deposit_max'):
                print(f"🔍 Applying deposit filters: min={filters.get('deposit_min')}, max={filters.get('deposit_max')}")
                
                try:
                    if filters.get('deposit_min'):
                        min_val = int(filters['deposit_min'])
                        print(f"🔍 Filtering deposit >= {min_val}")
                        
                        query = query.filter(
                            func.cast(
                                func.regexp_substr(self.model.first_deposit, '[0-9 ]+'),
                                'UNSIGNED'
                            ) >= min_val
                        )
                    
                    if filters.get('deposit_max'):
                        max_val = int(filters['deposit_max'])
                        print(f"🔍 Filtering deposit <= {max_val}")
                        
                        query = query.filter(
                            func.cast(
                                func.regexp_substr(self.model.first_deposit, '[0-9 ]+'),
                                'UNSIGNED'
                            ) <= max_val
                        )
                        
                except Exception as e:
                    print(f"❌ Erreur dans les filtres d'acompte: {e}")
                    # Version de fallback
                    try:
                        if filters.get('deposit_min'):
                            min_val = str(filters['deposit_min'])
                            query = query.filter(self.model.first_deposit.like(f'%{min_val}%'))
                            print(f"🔍 Fallback: searching for '{min_val}' in deposit field")
                    except:
                        print("❌ Even fallback failed for deposit filters")
                    pass
                               

            # Filtre par niveau RNCP
            if filters.get('rncp_level'):
                print(f"🔍 Applying rncp_level filter: {filters['rncp_level']}")
                query = query.filter(self.model.rncp_level == filters['rncp_level'])
            
            if filters.get('application_date'):
                print(f"🔍 Applying application_date filter: {filters['application_date']}")
                query = query.filter(self.model.application_date.ilike(f"%{filters['application_date']}%"))

            # Filtre par école
            if filters.get('school_id'):
                print(f"🔍 Applying school_id filter: {filters['school_id']}")
                query = query.filter(self.model.school_id == filters['school_id'])           


        # ✅ Compter le total après filtres
        total_count = query.count()
        print(f"🔍 Total programs after filters: {total_count}")
        
        # Appliquer la pagination
        offset = (page - 1) * limit
        programs = query.offset(offset).limit(limit).all()
        print(f"🔍 Retrieved {len(programs)} programs for page {page}")
        
        result = []
        for program in programs:
            try:
                program_data = program.as_dict_with_subdomains()
                if program.school:
                    program_data['school'] = program.school.as_dict()
                    result.append(program_data)
            except Exception as e:
                print(f"❌ Error processing program {program.id}: {e}")
        
        print(f"🔍 Final result: {len(result)} programs processed successfully")
        
        return {
            'data': result,
            'total': total_count,
            'page': page,
            'limit': limit,
            'pages': (total_count + limit - 1) // limit,
            'success': True  # ✅ Ajouter flag de succès
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
