class EvaluationCriteria:
    def __init__(self):
        # Define the thresholds for each score level for different criteria.
        criteria_type = [
            {"id": "cri001", "name": "Critères académiques"},
            {"id": "cri002", "name": "Critères linguistiques"},
            {"id": "cri003", "name": "Expérience professionnelle"},
            {"id": "cri004", "name": "Autres critères"}
        ]

        conditions = [ 
            # I-Score=0 
            # 1.Academic criteria
            {"id": "co0001", "name": "Moyenne générale < 10", "description": "Le candidat a une moyenne générale < 10/20", "score": 0, "criteria_type_id": "cri001", "comment": "Pour l'année la plus récente"},
            {"id": "co0002", "name": "Moyenne baccalauréat < 12", "description": "Le candidat a une moyenne générale inférieure à 12/20 au baccalauréat", "score": 0, "criteria_type_id": "cri001", "comment": "si ce candidat est en licence 2 ou moins"},
            {"id": "co0003", "name": "Moyenne générale < 10 sur 3 ans", "description": "Le candidat a cumulé une moyenne générale inférieure à 10 durant ses 3 dernières années ", "score": 0, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0004", "name": "Moyenne matières principales < 12", "description": "Le candidat a une moyenne générale inférieur à 12/20 dans ses matières principales durant les derniers trimestres/semestres", "score": 0, "criteria_type_id": "cri001", "comment": "le dernier ou l'avant-dernier trimestre/semestre"},
            {"id": "co0005", "name": "Mention bien au baccalauréat", "description": "Le candidat a obtenu moyenne générale > 14 au baccalauréat", "score": 5, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0006", "name": "Plus de 2 redoublements", "description": "Le candidat a plus de 2 redoublements durant ses 3 dernières années d'étude", "score": 0, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0007", "name": "Dettes de crédit", "description": "Le candidat a des dettes de crédit", "score": 0, "criteria_type_id": "cri001", "comment": "en bac+1 au moins"},
            # 2.Linguistic criteria
            {"id": "co0008", "name": "Niveau de français < B2", "description": "Le candidat a un niveau de français inférieure à B2", "score": 0, "criteria_type_id": "cri002", "comment": "<= B1"},
            # 3.Other criteria
            {"id": "co0009", "name": "Preuves financières insuffisantes", "description": "Les preuves financières du candidat sont insuffisantes", "score": 0, "criteria_type_id": "cri004", "comment": ""},

            # II-Score=1 
            {"id": "co0010", "name": "Moyenne générale < 11", "description": "Le candidat a une moyenne générale < 11/20", "score": 1, "criteria_type_id": "cri001", "comment": "Pour l'année la plus récente"},
            {"id": "co0011", "name": "Moyenne générale < 11 sur 3 ans", "description": "Le candidat a cumulé une moyenne générale inférieure à 11 durant ses 3 dernières années ", "score": 1, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0012", "name": "Moyenne matières principales < 11", "description": "Le candidat a une moyenne générale inférieur à 11/20 dans ses matières principales durant les derniers trimestres/semestres", "score": 1, "criteria_type_id": "cri001", "comment": "des 2 dernières années"},
            {"id": "co0013", "name": "Performances stables sur 2 ans", "description": "Les performances du candidat sont restées au même niveau pendant ces deux années", "score": 1, "criteria_type_id": "cri001", "comment": ""},

            # III-Score=2 
            {"id": "co0014", "name": "Moyenne générale 11-12", "description": "Le candidat a une moyenne générale entre 11 et 12/20", "score": 2, "criteria_type_id": "cri001", "comment": "Pour l'année la plus récente"},
            {"id": "co0015", "name": "Moyenne générale 11-12 sur 3 ans", "description": "Le candidat a cumulé une moyenne générale entre 11 et 12 durant ses 3 dernières années ", "score": 2, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0016", "name": "Moyenne matières principales 11-12", "description": "Le candidat a une moyenne générale entre 11 et 12/20 dans ses matières principales durant les derniers trimestres/semestres", "score": 2, "criteria_type_id": "cri001", "comment": "des 2 dernières années"},
            {"id": "co0017", "name": "Moyennes stables sur 3 ans", "description": "Les moyennes du candidat sont restées stables sur trois années consécutives", "score": 2, "criteria_type_id": "cri001", "comment": ""},

            # IV-Score=2.5 
            {"id": "co0018", "name": "Moyenne générale 12-13", "description": "Le candidat a une moyenne générale entre 12 et 13/20", "score": 2.5, "criteria_type_id": "cri001", "comment": "Pour l'année la plus récente"},
            {"id": "co0019", "name": "Moyenne générale 12-13 sur 3 ans", "description": "Le candidat a cumulé une moyenne générale entre 12 et 13 durant ses 3 dernières années ", "score": 2.5, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0020", "name": "Moyenne matières principales 12-13", "description": "Le candidat a une moyenne générale entre 12 et 13/20 dans ses matières principales durant les derniers trimestres/semestres", "score": 2.5, "criteria_type_id": "cri001", "comment": "des 2 dernières années"},        

            # V-Score=3 
            {"id": "co0021", "name": "Moyenne générale 13-14", "description": "Le candidat a une moyenne générale entre 13 et 14/20", "score": 3, "criteria_type_id": "cri001", "comment": "Pour l'année la plus récente"},
            {"id": "co0022", "name": "Moyenne générale 13-14 sur 3 ans", "description": "Le candidat a cumulé une moyenne générale entre 13 et 14 durant ses 3 dernières années ", "score": 3, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0023", "name": "Moyenne matières principales 13-14", "description": "Le candidat a une moyenne générale entre 13 et 14/20 dans ses matières principales durant les derniers trimestres/semestres", "score": 3, "criteria_type_id": "cri001", "comment": "des 2 dernières années"},
            {"id": "co0024", "name": "Progression continue sur 3 ans 13-14", "description": "Le candidat a vu ses moyennes progresser régulièrement ces trois dernières années, se situant désormais entre 13 et 14/20.", "score": 3, "criteria_type_id": "cri001", "comment": "Verifier s'il y'a eu progression régulière au cours des dernières années et si la moyenne actuelle est entre 13 et 14/20"},

            #1.linguistic criteria  
            {"id": "co0025", "name": "Niveau de français B2", "description": "Le candidat a un niveau de français B2", "score": 2.5, "criteria_type_id": "cri002", "comment": ""},
            #2.Other criteria
            {"id": "co0026", "name": "Expérience professionnelle 3+ mois", "description": "Le candidat connaît une expérience professionnelle dans sont domaine d'étude", "score": 3, "criteria_type_id": "cri003", "comment": "stage ou emploi partiel de plus de 3 mois"},

            # VI-Score=3.5 
            {"id": "co0027", "name": "Moyenne générale 14-15", "description": "Le candidat a une moyenne générale entre 14 et 15/20", "score": 3.5, "criteria_type_id": "cri001", "comment": "Pour l'année la plus récente"},
            {"id": "co0028", "name": "Moyenne générale 14-15 sur 3 ans", "description": "Le candidat a cumulé une moyenne générale entre 14 et 15 durant ses 3 dernières années ", "score": 3.5, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0029", "name": "Moyenne matières principales 14-15", "description": "Le candidat a une moyenne générale entre 14 et 15/20 dans ses matières principales durant les derniers trimestres/semestres", "score": 3.5, "criteria_type_id": "cri001", "comment": "des 2 dernières années"},
            {"id": "co0030", "name": "Progression continue sur 3 ans 14-15", "description": "Le candidat a vu ses moyennes progresser régulièrement ces trois dernières années, se situant désormais entre 14 et 15/20.", "score": 3.5, "criteria_type_id": "cri001", "comment": "Verifier s'il y'a eu progression régulière au cours des dernières années et si la moyenne actuelle est entre 14 et 15/20"},
            {"id": "co0031", "name": "Mention bien au baccalauréat (>14)", "description": "Le candidat a obtenu une mention très bien au baccalauréat", "score": 3.5, "criteria_type_id": "cri001", "comment": "si ce candidat est en licence 2 ou moins"},

            #1.linguistic criteria
            {"id": "co0032", "name": "Niveau de français >= C1", "description": "Le candidat a un niveau de français supérieur à B2", "score": 3.5, "criteria_type_id": "cri002", "comment": ""},
            #2.Other criteria
            {"id": "co0033", "name": "Séjours en France/Schengen", "description": "Le candidat a déjà séjourné en France ou dans l'espace Schengen", "score": 3.5, "criteria_type_id": "cri004", "comment": "bourses ou séjours antérieurs en France"},
            {"id": "co0034", "name": "Niveau d'anglais > B1", "description": "Le candidat a un niveau d'anglais supérieur à B1", "score": 3.5, "criteria_type_id": "cri004", "comment": ""},
            {"id": "co0035", "name": "Expérience professionnelle 6+ mois", "description": "Le candidat peut certifier d'une expérience professionnelle dans son domaine d'étude", "score": 4, "criteria_type_id": "cri003", "comment": "stage ou emploi partiel de plus de 6 mois"},

            # VII-Score=3.75 
            {"id": "co0036", "name": "Moyenne générale 15-16", "description": "Le candidat a une moyenne générale entre 15 et 16/20", "score": 3.75, "criteria_type_id": "cri001", "comment": "Pour l'année la plus récente"},
            {"id": "co0037", "name": "Moyenne générale 15-16 sur 3 ans", "description": "Le candidat a cumulé une moyenne générale entre 15 et 16 durant ses 3 dernières années ", "score": 3.75, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0038", "name": "Moyenne matières principales 15-16", "description": "Le candidat a une moyenne générale entre 15 et 16/20 dans ses matières principales durant les derniers trimestres/semestres", "score": 3.75, "criteria_type_id": "cri001", "comment": "des 2 dernières années"}, 
            {"id": "co0039", "name": "Progression continue sur 3 ans 15-16", "description": "Le candidat a vu ses moyennes progresser régulièrement ces trois dernières années, se situant désormais entre 15 et 16/20.", "score": 3.75, "criteria_type_id": "cri001", "comment": "Verifier s'il y'a eu progression régulière au cours des dernières années et si la moyenne actuelle est entre 15 et 16/20"},
            
            # VIII-Score=4 
            {"id": "co0040", "name": "Moyenne générale 16-17", "description": "Le candidat a une moyenne générale entre 16 et 17/20", "score": 4, "criteria_type_id": "cri001", "comment": "Pour l'année la plus récente"},
            {"id": "co0041", "name": "Moyenne générale 16-17 sur 3 ans", "description": "Le candidat a cumulé une moyenne générale entre 16 et 17 durant ses 3 dernières années ", "score": 4, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0042", "name": "Moyenne matières principales 16-17", "description": "Le candidat a une moyenne générale entre 16 et 17/20 dans ses matières principales durant les derniers trimestres/semestres", "score": 4, "criteria_type_id": "cri001", "comment": "des 2 dernières années"},
            {"id": "co0043", "name": "Progression continue sur 3 ans 16-17", "description": "Le candidat a vu ses moyennes progresser régulièrement ces trois dernières années, se situant désormais entre 16 et 17/20.", "score": 4, "criteria_type_id": "cri001", "comment": "Verifier s'il y'a eu progression régulière au cours des dernières années et si la moyenne actuelle est entre 16 et 17/20"},    
            {"id": "co0044", "name": "Mention très bien au baccalauréat (>16)", "description": "Le candidat a obtenu une mention très bien au baccalauréat", "score": 4, "criteria_type_id": "cri001", "comment": "si ce candidat est en licence 2 ou moins"},
        
            #1.Other criteria
            {"id": "co0045", "name": "Expérience professionnelle 1+ an", "description": "Le candidat peut certifier d'une expérience professionnelle dans son domaine d'étude", "score": 4, "criteria_type_id": "cri003", "comment": "stage ou emploi de plus de 1 an"},
            {"id": "co0046", "name": "Distinction dans les matières principales", "description": "Le candidat a été honoré d'une récompense", "score": 4, "criteria_type_id": "cri003", "comment": ""},
            
            # IX-Score=4.5 
            {"id": "co0047", "name": "Moyenne générale 17-18", "description": "Le candidat a une moyenne générale entre 17 et 18/20", "score": 4.5, "criteria_type_id": "cri001", "comment": "Pour l'année la plus récente"},
            {"id": "co0048", "name": "Moyenne générale 17-18 sur 3 ans", "description": "Le candidat a cumulé une moyenne générale entre 17 et 18 durant ses 3 dernières années ", "score": 4.5, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0049", "name": "Moyenne matières principales 17-18", "description": "Le candidat a une moyenne générale entre 17 et 18/20 dans ses matières principales durant les derniers trimestres/semestres", "score": 4.5, "criteria_type_id": "cri001", "comment": "des 2 dernières années"},
            {"id": "co0050", "name": "Progression continue sur 3 ans 17-18", "description": "Le candidat a vu ses moyennes progresser régulièrement ces trois dernières années, se situant désormais entre 17 et 18/20.", "score": 4.5, "criteria_type_id": "cri001", "comment": "Verifier s'il y'a eu progression régulière au cours des dernières années et si la moyenne actuelle est entre 1713 et 18/20"},    

            # X-Score=5 
            {"id": "co0051", "name": "Moyenne générale > 18", "description": "Le candidat a une moyenne générale > 18/20", "score": 5, "criteria_type_id": "cri001", "comment": "Pour l'année la plus récente"},
            {"id": "co0052", "name": "Moyenne générale > 18 sur 3 ans", "description": "Le candidat a cumulé une moyenne générale > 18 durant ses 3 dernières années ", "score": 5, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0053", "name": "Moyenne matières principales > 18", "description": "Le candidat a une moyenne générale > 18/20 dans ses matières principales durant les derniers trimestres/semestres", "score": 5, "criteria_type_id": "cri001", "comment": "des 2 dernières années"},
            {"id": "co0054", "name": "Mention excellente au baccalauréat (>17)", "description": "Le candidat a obtenu une mention excellente au baccalauréat", "score": 5, "criteria_type_id": "cri001", "comment": "si ce candidat est en licence 2 ou moins"},
            # Classement
            {"id": "co0055", "name": "Classement au > 20", "description": "Le candidat se situe au dessus de la 20ème place", "score": 1, "criteria_type_id": "cri001", "comment": "sur les 2 dernières années si disponible"},
            {"id": "co0056", "name": "Classement au > 15", "description": "Le candidat se situe au dessus de la 15ème place", "score": 2, "criteria_type_id": "cri001", "comment": "sur les 2 dernières années si disponible"},
            {"id": "co0057", "name": "Classement au > 10", "description": "Le candidat se situe au dessus de la 00ème place", "score": 2.5, "criteria_type_id": "cri001", "comment": "sur les 2 dernières années si disponible si disponible"},
            {"id": "co0058", "name": "Classement au > 5", "description": "Le candidat se situe au dessus de la 5ème place", "score": 3, "criteria_type_id": "cri001", "comment": "sur les 2 dernières années si disponible"},
            {"id": "co0059", "name": "Classement au > 3", "description": "Le candidat se situe au dessus de 3ème place", "score": 3.5, "criteria_type_id": "cri001", "comment": "sur les 2 dernières années si disponible"},
            {"id": "co0060", "name": "Classement au = 3", "description": "Le candidat occupe la 3ème place", "score": 4, "criteria_type_id": "cri001", "comment": "sur les 2 dernières années si disponible"},
            {"id": "co0061", "name": "Classement au = 2", "description": "Le candidat occupe la 2ème place", "score": 4.5, "criteria_type_id": "cri001", "comment": "sur les 2 dernières années si disponible"}, 
            {"id": "co0061", "name": "Classement au = 1", "description": "Le candidat occupe la 1ère place", "score": 5, "criteria_type_id": "cri001", "comment": "sur les 2 dernières années si disponible"},        
        ]

        self.academic_criteria = {
            0: {"id": "A1", "conditions": ["Moyenne générale < 10", "Moyenne baccalauréat < 10", "Plus de deux redoublements", ""]},
            1: {"id": "A2", "conditions": ["Moyenne générale < 11", "Moyenne baccalauréat < 12"]},
            2: {"id": "A3", "conditions": ["Moyenne générale entre 11 et 12"]},
            3: ["Moyenne générale entre 12 et 13"],
            4: ["Moyenne générale entre 13 et 15"],
            4.5: ["Moyenne générale entre 15 et 16"],
            5: ["Moyenne générale > 16"]
        }
        
        self.linguistic_criteria = {
            0: ["Niveau de français < B1"],
            2: ["Niveau de français B1"],
            3: ["Niveau de français B2"],
            4: ["Niveau de français C1"],
            5: ["Niveau de français C2"]
        }
        
        self.professional_experience_criteria = {
            0: ["Aucune expérience professionnelle"],
            2: ["Expérience professionnelle limitée"],
            3: ["Stage ou emploi partiel dans le domaine"],
            4: ["Expérience significative"],
            5: ["Expérience exceptionnelle avec réalisations majeures"]
        }
        
        self.other_criteria = {
            0: ["Pas de motivation ou preuves financières insuffisantes"],
            2: ["Motivation présente mais floue"],
            3: ["Bonne motivation, ressources financières suffisantes"],
            4: ["Lettre de motivation très convaincante"],
            5: ["Motivation exceptionnelle, bourses ou séjours antérieurs en France"]
        }

        # Define the thresholds for each score level for different criteria.
        self.criteria_type = [
            {"id": "cri001", "name": "Critères académiques"},
            {"id": "cri002", "name": "Critères linguistiques"},
            {"id": "cri003", "name": "Expérience professionnelle"},
            {"id": "cri004", "name": "Autres critères"}
        ]

        self.conditions = [
            # I-Score 0 Case
            {"id": "co0001", "name": "Moyenne générale < 10/20", "description": "Le candidat a une moyenne générale < 10/20", "score": 0, "criteria_type_id": "cri001", "comment": "Pour l'année la plus récente"},
            {"id": "co0002", "name": "Moyenne générale < 12/20 au baccalauréat", "description": "Le candidat a une moyenne générale inférieure à 12/20 au baccalauréat", "score": 0, "criteria_type_id": "cri001", "comment": "si ce candidat est en licence 2 ou moins"},
            {"id": "co0003", "name": "Moyenne cumulée < 10 sur 3 ans", "description": "Le candidat a cumulé une moyenne générale inférieure à 10 durant ses 3 dernières années", "score": 0, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0004", "name": "Moyenne principale < 12/20", "description": "Le candidat a une moyenne générale inférieure à 12/20 dans ses matières principales durant les derniers trimestres/semestres", "score": 0, "criteria_type_id": "cri001", "comment": "le dernier ou l'avant-dernier trimestre/semestre"},
            {"id": "co0005", "name": "Notes du baccalauréat non renseignées", "description": "Le candidat n'a pas renseigné ses notes du baccalauréat", "score": 0, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0006", "name": ">2 redoublements en 3 ans", "description": "Le candidat a plus de 2 redoublements durant ses 3 dernières années d'étude", "score": 0, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0007", "name": "Dettes de crédit", "description": "Le candidat a des dettes de crédit", "score": 0, "criteria_type_id": "cri001", "comment": "en bac+1 au moins"},
            {"id": "co0008", "name": "Niveau de français < B2", "description": "Le candidat a un niveau de français inférieure à B2", "score": 0, "criteria_type_id": "cri002", "comment": "<= B1"},
            {"id": "co0009", "name": "Preuves financières insuffisantes", "description": "Les preuves financières du candidat sont insuffisantes", "score": 0, "criteria_type_id": "cri004", "comment": ""},

            # II-Score 1 Case
            {"id": "co0010", "name": "Moyenne générale < 11/20", "description": "Le candidat a une moyenne générale < 11/20", "score": 1, "criteria_type_id": "cri001", "comment": "Pour l'année la plus récente"},
            {"id": "co0011", "name": "Moyenne cumulée < 11 sur 3 ans", "description": "Le candidat a cumulé une moyenne générale inférieure à 11 durant ses 3 dernières années", "score": 1, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0012", "name": "Moyenne principale < 11/20", "description": "Le candidat a une moyenne générale inférieure à 11/20 dans ses matières principales durant les derniers trimestres/semestres", "score": 1, "criteria_type_id": "cri001", "comment": "le dernier ou l'avant-dernier trimestre/semestre"},
            {"id": "co0013", "name": "Performances stables sur deux ans", "description": "Les performances du candidat sont restées au même niveau pendant ces deux années", "score": 1, "criteria_type_id": "cri001", "comment": ""},

            # III-Score 2 Case
            {"id": "co0014", "name": "Moyenne générale entre 11 et 12/20", "description": "Le candidat a une moyenne générale entre 11 et 12/20", "score": 2, "criteria_type_id": "cri001", "comment": "Pour l'année la plus récente"},
            {"id": "co0015", "name": "Moyenne cumulée entre 11 et 12 sur 3 ans", "description": "Le candidat a cumulé une moyenne générale entre 11 et 12 durant ses 3 dernières années", "score": 2, "criteria_type_id": "cri001", "comment": ""},
            {"id": "co0016", "name": "Moyenne principale entre 11 et 12/20", "description": "Le candidat a une moyenne générale entre 11 et 12/20 dans ses matières principales durant les derniers trimestres/semestres", "score": 2, "criteria_type_id": "cri001", "comment": "le dernier ou l'avant-dernier trimestre/semestre"},
            {"id": "co0017", "name": "Moyennes stables sur trois ans", "description": "Les moyennes du candidat sont restées stables sur trois années consécutives", "score": 2, "criteria_type_id": "cri001", "comment": ""}
            # Continue adding other conditions similarly...
        ]

    def evaluate(self, candidate_profile):
        final_score = 5  # Start with the highest possible score
        for condition in self.conditions:
            if condition['id'].lower() in candidate_profile.lower():
                if condition['score'] == 0:
                    return 0  # If any score is 0, the final score is 0
                final_score = min(final_score, condition['score'])
        return final_score

# Example of candidate profile
candidate_profile = "Le candidat a une moyenne générale < 10/20; Le candidat a un niveau de français inférieur à B2"

# Evaluate the candidate
evaluator = EvaluationCriteria()
score = evaluator.evaluate(candidate_profile)
print(f"Le score final du candidat est: {score}/5")
