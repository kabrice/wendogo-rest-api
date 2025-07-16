# common/services/domain_service.py - Version avec tables de cache DB

from common.models.domain import Domain
from common.models.subdomain import Subdomain
from common.models.program import Program
from common.models.school import School
from common.models import db
from sqlalchemy import exists, distinct, text

class DomainService:
    """Service pour gérer la logique métier des domaines"""
    
    @staticmethod
    def get_domains_with_active_programs_optimized():
        """
        Version ULTRA OPTIMISÉE avec tables de cache
        """
        try:
            # ✅ NOUVEAU: Utiliser les tables de cache si elles existent
            if DomainService._cache_tables_exist():
                return DomainService._get_domains_from_cache_tables()
            else:
                # Fallback vers l'ancienne méthode
                print("⚠️ Cache tables not found, using fallback method")
                return DomainService._get_domains_legacy_method()
        except Exception as e:
            print(f"❌ Error in optimized method: {e}")
            # Fallback vers l'ancienne méthode
            return DomainService._get_domains_legacy_method()
    
    @staticmethod
    def _cache_tables_exist():
        """Vérifie si les tables de cache existent"""
        try:
            result = db.session.execute(text(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_name = 'domain_program_counts' "
                "AND table_schema = DATABASE()"
            )).fetchone()
            return result is not None
        except:
            return False
    
    @staticmethod
    def _get_domains_from_cache_tables():
        """Récupère les domaines depuis les tables de cache - ULTRA RAPIDE"""
        print("✅ Using cache tables for domains")
        
        # Requête SQL optimisée avec les tables de cache
        query = text("""
            SELECT 
                d.id,
                d.name,
                d.level_id,
                COALESCE(dc.program_count, 0) as total_programs
            FROM domain d
            LEFT JOIN domain_program_counts dc ON dc.domain_id = d.id
            WHERE COALESCE(dc.program_count, 0) > 0
            ORDER BY dc.program_count DESC
        """)
        
        domains_result = db.session.execute(query).fetchall()
        result = []
        
        for domain_row in domains_result:
            domain_data = {
                'id': domain_row.id,
                'name': domain_row.name,
                'level_id': domain_row.level_id,
                'total_programs': domain_row.total_programs
            }
            
            # Récupérer les sous-domaines avec cache
            subdomains_query = text("""
                SELECT 
                    sd.id,
                    sd.name,
                    sd.domain_id,
                    COALESCE(sdc.program_count, 0) as program_count
                FROM subdomain sd
                LEFT JOIN subdomain_program_counts sdc ON sdc.subdomain_id = sd.id
                WHERE sd.domain_id = :domain_id 
                AND COALESCE(sdc.program_count, 0) > 0
                ORDER BY sdc.program_count DESC
            """)
            
            subdomains_result = db.session.execute(
                subdomains_query, 
                {'domain_id': domain_row.id}
            ).fetchall()
            
            active_subdomains = []
            for subdomain_row in subdomains_result:
                subdomain_data = {
                    'id': subdomain_row.id,
                    'name': subdomain_row.name,
                    'domain_id': subdomain_row.domain_id,
                    'program_count': subdomain_row.program_count
                }
                active_subdomains.append(subdomain_data)
            
            if active_subdomains:
                domain_data['subdomains'] = active_subdomains
                result.append(domain_data)
        
        print(f"✅ Retrieved {len(result)} domains with cache tables in ~10-50ms")
        return result
    
    @staticmethod
    def _get_domains_legacy_method():
        """Ancienne méthode (fallback) - LENTE mais fiable"""
        print("🔄 Using legacy method for domains")
        
        from sqlalchemy import func, distinct, or_
        
        # Récupérer tous les domaines
        all_domains = Domain.query.all()
        result = []
        
        for domain in all_domains:
            domain_data = domain.as_dict()
            active_subdomains = []
            
            # Pour chaque sous-domaine de ce domaine
            for subdomain in domain.subdomains:
                # REQUÊTE LENTE - Compter les programmes distincts
                distinct_programs = (
                    Program.query
                    .join(School, Program.school_id == School.id)
                    .filter(
                        Program.is_active == True,
                        School.is_public == False,
                        or_(
                            Program.sub_domain1_id == subdomain.id,
                            Program.sub_domain2_id == subdomain.id,
                            Program.sub_domain3_id == subdomain.id
                        )
                    )
                    .with_entities(Program.id)
                    .distinct()
                    .all()
                )
                
                program_count = len(distinct_programs)
                
                if program_count > 0:
                    subdomain_data = subdomain.as_dict()
                    subdomain_data['program_count'] = program_count
                    active_subdomains.append(subdomain_data)
            
            # Ajouter le domaine seulement s'il a des sous-domaines avec programmes
            if active_subdomains:
                domain_data['subdomains'] = active_subdomains
                
                # Calculer le total sans double comptage
                all_subdomain_ids = [sub['id'] for sub in active_subdomains]
                
                total_distinct_programs = (
                    Program.query
                    .join(School, Program.school_id == School.id)
                    .filter(
                        Program.is_active == True,
                        School.is_public == False,
                        or_(
                            Program.sub_domain1_id.in_(all_subdomain_ids),
                            Program.sub_domain2_id.in_(all_subdomain_ids),
                            Program.sub_domain3_id.in_(all_subdomain_ids)
                        )
                    )
                    .with_entities(Program.id)
                    .distinct()
                    .count()
                )
                
                domain_data['total_programs'] = total_distinct_programs
                result.append(domain_data)
        
        # Trier par nombre total de programmes
        result.sort(key=lambda x: x['total_programs'], reverse=True)
        
        print(f"✅ Retrieved {len(result)} domains with legacy method in ~2-5 seconds")
        return result
    
    @staticmethod
    def get_subdomain_program_count(subdomain_id):
        """Récupère le nombre de programmes pour un sous-domaine"""
        try:
            if DomainService._cache_tables_exist():
                # Version optimisée avec cache
                result = db.session.execute(text(
                    "SELECT program_count FROM subdomain_program_counts WHERE subdomain_id = :id"
                ), {'id': subdomain_id}).fetchone()
                return result.program_count if result else 0
            else:
                # Fallback vers calcul en temps réel
                from sqlalchemy import or_
                return (
                    Program.query
                    .join(School, Program.school_id == School.id)
                    .filter(
                        Program.is_active == True,
                        School.is_public == False,
                        or_(
                            Program.sub_domain1_id == subdomain_id,
                            Program.sub_domain2_id == subdomain_id,
                            Program.sub_domain3_id == subdomain_id
                        )
                    )
                    .with_entities(Program.id)
                    .distinct()
                    .count()
                )
        except Exception as e:
            print(f"❌ Error getting subdomain count: {e}")
            return 0
    
    @staticmethod
    def get_domain_program_count(domain_id):
        """Récupère le nombre total de programmes pour un domaine"""
        try:
            if DomainService._cache_tables_exist():
                # Version optimisée avec cache
                result = db.session.execute(text(
                    "SELECT program_count FROM domain_program_counts WHERE domain_id = :id"
                ), {'id': domain_id}).fetchone()
                return result.program_count if result else 0
            else:
                # Fallback vers calcul en temps réel
                subdomain_ids = [
                    sub.id for sub in Subdomain.query.filter_by(domain_id=domain_id).all()
                ]
                
                if not subdomain_ids:
                    return 0
                
                from sqlalchemy import or_
                return (
                    Program.query
                    .join(School, Program.school_id == School.id)
                    .filter(
                        Program.is_active == True,
                        School.is_public == False,
                        or_(
                            Program.sub_domain1_id.in_(subdomain_ids),
                            Program.sub_domain2_id.in_(subdomain_ids),
                            Program.sub_domain3_id.in_(subdomain_ids)
                        )
                    )
                    .with_entities(Program.id)
                    .distinct()
                    .count()
                )
        except Exception as e:
            print(f"❌ Error getting domain count: {e}")
            return 0
    
    @staticmethod
    def refresh_cache_tables():
        """Force la mise à jour des tables de cache"""
        try:
            if DomainService._cache_tables_exist():
                print("🔄 Refreshing cache tables...")
                
                # Appeler les procédures stockées
                db.session.execute(text("CALL RefreshDomainCounts()"))
                db.session.execute(text("CALL RefreshSubdomainCounts()"))
                db.session.commit()
                
                print("✅ Cache tables refreshed successfully")
                return True
            else:
                print("⚠️ Cache tables don't exist, cannot refresh")
                return False
        except Exception as e:
            print(f"❌ Error refreshing cache tables: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_total_programs_count():
        """Récupère le nombre total de programmes actifs"""
        return (
            Program.query
            .join(School, Program.school_id == School.id)
            .filter(
                Program.is_active == True,
                School.is_public == False
            )
            .count()
        )
