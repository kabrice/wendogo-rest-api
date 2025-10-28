# common/routes/school_route.py (mis à jour)
from common.models.school import School
from sqlalchemy import or_

class SchoolDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_schools_from_ids(self, school_ids):
        """Méthode existante - Récupère plusieurs écoles par leurs IDs"""
        schools = self.model.query.filter(self.model.id.in_(school_ids)).all()
        return [school.as_dict() for school in schools]
    
    def get_all_schools(self):
        """Récupère toutes les écoles publiques"""
        schools = self.model.query.filter_by(is_public=False).all()
        return [school.as_dict() for school in schools]
    
    def get_school_by_id(self, school_id):
        """Récupère une école par son ID"""
        school = self.model.query.filter_by(id=school_id).first()
        return school
    
    def get_school_by_slug(self, slug):
        """Récupère une école par son slug"""
        school = self.model.query.filter_by(slug=slug).first()
        return school
    
    def get_all_school_slugs(self):
        """Récupère tous les slugs des écoles publiques"""
        schools = self.model.query.filter_by(is_public=False).with_entities(self.model.slug).all()
        return [school.slug for school in schools]
    
    def search_schools(self, filters=None):
        """Recherche d'écoles avec filtres"""
        query = self.model.query.filter_by(is_public=False)
        
        if filters:
            # Filtre par texte de recherche
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        self.model.name.ilike(search_term),
                        self.model.description.ilike(search_term),
                        self.model.school_group.ilike(search_term)
                    )
                )
            
            # Filtre par ville
            if filters.get('city'):
                query = query.filter_by(base_city=filters['city'])
            
            # Filtre Campus France
            if filters.get('campus_france') is not None:
                query = query.filter_by(connection_campus_france=filters['campus_france'])
            
            # Filtre hors contrat
            if filters.get('hors_contrat') is not None:
                query = query.filter_by(hors_contrat=filters['hors_contrat'])
        
        schools = query.all()
        return [school.as_dict() for school in schools]
 
    def get_similar_schools(self, school_id, limit=3, locale='fr'):
        """Récupère les écoles similaires avec stratégie basée sur les sous-domaines"""
        import re
        from common.models.program import Program
        from sqlalchemy import func, distinct, or_
        
        current_school = self.model.query.filter_by(id=school_id).first()
        if not current_school:
            return []
        
        # 1. RÉCUPÉRER LES SOUS-DOMAINES DE L'ÉCOLE COURANTE
        current_subdomains = set()
        current_programs = Program.query.filter_by(
            school_id=school_id, 
            is_active=True
        ).all()
        
        for program in current_programs:
            for subdomain_field in [program.sub_domain1_id, program.sub_domain2_id, program.sub_domain3_id]:
                if subdomain_field:
                    current_subdomains.add(subdomain_field)
        
        print(f"École {current_school.name} - Sous-domaines: {current_subdomains}")
        
        # 2. TROUVER LES ÉCOLES AVEC SOUS-DOMAINES COMMUNS
        other_schools = (self.model.query
                        .filter(
                            self.model.id != school_id,
                            self.model.is_public == False
                        )
                        .all())
        
        school_scores = []
        current_description = (current_school.description or "").lower()
        
        for school in other_schools:
            similarity_score = 0.0
            
            # 1. PRIORITÉ MAXIMALE : SOUS-DOMAINES COMMUNS (jusqu'à 13 points)
            school_subdomains = set()
            school_programs = Program.query.filter_by(
                school_id=school.id, 
                is_active=True
            ).all()
            
            for program in school_programs:
                for subdomain_field in [program.sub_domain1_id, program.sub_domain2_id, program.sub_domain3_id]:
                    if subdomain_field:
                        school_subdomains.add(subdomain_field)
            
            # Calculer la similarité Jaccard des sous-domaines
            if current_subdomains and school_subdomains:
                common_subdomains = current_subdomains & school_subdomains
                total_subdomains = current_subdomains | school_subdomains
                jaccard_similarity = len(common_subdomains) / len(total_subdomains)
                
                # Score basé sur Jaccard (0-10 points)
                similarity_score += jaccard_similarity * 10
                
                # Bonus pour beaucoup de sous-domaines communs
                similarity_score += min(3, len(common_subdomains) * 0.5)
            
            # 2. VILLE (3 points)
            if school.base_city == current_school.base_city:
                similarity_score += 3
            
            # 3. GROUPE D'ÉCOLE (3 points)
            if school.school_group and current_school.school_group:
                if school.school_group == current_school.school_group:
                    similarity_score += 3
            
            # 4. STRATÉGIE INTELLIGENTE POUR LA DESCRIPTION
            school_description = (school.description or "").lower()
            if current_description and school_description:
                
                # A. Extraction automatique de concepts
                description_score = 0
                
                # Concepts techniques (détectés automatiquement)
                tech_concepts = [
                    'ingénieur', 'technolog', 'innovat', 'recherche', 'digital', 
                    'numérique', 'industri', 'électron', 'informatique', 'ia',
                    'intelligence artificielle', 'data', 'cybersécurité'
                ]
                
                # Concepts business/management
                business_concepts = [
                    'management', 'gestion', 'commerce', 'business', 'marketing',
                    'finance', 'entrepreneuriat', 'économ', 'admin'
                ]
                
                # Concepts spécialisés
                specialized_concepts = [
                    'médical', 'santé', 'pharmacie', 'vétérinaire', 'agronom',
                    'architecture', 'design', 'art', 'communication', 'journalisme',
                    'droit', 'juridique', 'transport', 'logistique', 'énergie'
                ]
                
                # Concepts internationaux
                international_concepts = [
                    'international', 'européen', 'mondial', 'global', 'mobilité',
                    'étranger', 'anglais', 'bilingue', 'multiculturel'
                ]
                
                # Concepts qualité/prestige
                quality_concepts = [
                    'excellence', 'prestigieux', 'reconnu', 'accrédité', 'certifié',
                    'partenariat', 'réseau', 'leader', 'référence'
                ]
                
                all_concept_groups = [
                    tech_concepts, business_concepts, specialized_concepts,
                    international_concepts, quality_concepts
                ]
                
                # Calculer score par groupe de concepts
                for concept_group in all_concept_groups:
                    current_has = any(concept in current_description for concept in concept_group)
                    school_has = any(concept in school_description for concept in concept_group)
                    if current_has and school_has:
                        description_score += 0.8  # Max 4 points pour tous les groupes
                
                # B. Analyse des mots-clés dynamique
                # Extraire les mots importants (> 5 caractères, non stop-words)
                stop_words = {'dans', 'avec', 'pour', 'sont', 'des', 'les', 'une', 'ses', 'son', 'leur', 'cette', 'ces', 'formation', 'école', 'étudiant'}
                
                try:
                    current_words = set(re.findall(r'\b\w{5,}\b', current_description))
                    school_words = set(re.findall(r'\b\w{5,}\b', school_description))
                    
                    # Enlever les stop words
                    current_words -= stop_words
                    school_words -= stop_words
                    
                    # Calculer intersection
                    common_words = current_words & school_words
                    if len(common_words) > 0 and (len(current_words) > 0 or len(school_words) > 0):
                        word_similarity = len(common_words) / max(len(current_words), len(school_words))
                        description_score += word_similarity * 2  # Max 2 points
                except Exception as e:
                    print(f"Erreur analyse mots-clés: {e}")
                
                similarity_score += min(4, description_score)  # Cap à 4 points pour description
            
            # 5. CAMPUS FRANCE (1 point)
            if school.connection_campus_france == current_school.connection_campus_france:
                similarity_score += 1
            
            # 6. STATUT CONTRAT (1 point)
            if school.hors_contrat == current_school.hors_contrat:
                similarity_score += 1
            
            # 7. TAUX INTERNATIONAL SIMILAIRE (1 point)
            if school.international_student_rate and current_school.international_student_rate:
                try:
                    school_match = re.search(r'\d+', str(school.international_student_rate))
                    current_match = re.search(r'\d+', str(current_school.international_student_rate))
                    
                    if school_match and current_match:
                        school_rate = float(school_match.group())
                        current_rate = float(current_match.group())
                        if abs(school_rate - current_rate) < 20:
                            similarity_score += 1
                except Exception as e:
                    print(f"Erreur taux international: {e}")
            
            # 8. NOMBRE DE PROGRAMMES SIMILAIRE (0.5 point)
            current_program_count = len(current_programs)
            school_program_count = len(school_programs)
            if current_program_count > 0 and school_program_count > 0:
                ratio = min(current_program_count, school_program_count) / max(current_program_count, school_program_count)
                if ratio > 0.5:  # Taille similaire
                    similarity_score += 0.5
            
            # Ajouter seulement si score significatif
            if similarity_score > 1.0:  # Seuil plus élevé pour éliminer le bruit
                school_scores.append((school, similarity_score))
        
        # Trier par score et retourner les meilleurs
        school_scores.sort(key=lambda x: x[1], reverse=True)
        result = []
        
        for school, score in school_scores[:limit]:
            school_data = school.as_dict()
            school_data['similarity_score'] = round(score, 2)
            result.append(school_data)
        
        print(f"Écoles similaires trouvées: {[(s['name'], s['similarity_score']) for s in result]}")
        return result

    def get_schools_preview(self):
        """Récupère un aperçu des écoles (données limitées)"""
        schools = self.model.query.filter_by(is_public=False).all()
        result = []
        for school in schools:
            preview = {
                'id': school.id,
                'slug': school.slug,
                'name': school.name,
                'school_group': school.school_group,
                'base_city': school.base_city,
                'logo_path': school.logo_path,
                'connection_campus_france': school.connection_campus_france,
                'international_student_rate': school.international_student_rate,
                'alternance_rate': school.alternance_rate,
                'hors_contrat': school.hors_contrat
            }
            result.append(preview)
        return result
    
    def get_schools_count(self):
        """Récupère le nombre total d'écoles publiques"""
        return self.model.query.filter_by(is_public=False).count()  # is_public=False pour écoles privées

school_dao = SchoolDAO(School)
