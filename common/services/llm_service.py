import requests
import json
import os
from openai import OpenAI

# Configuration des API Keys
DEEPSEEK_API_URL_CHAT = "https://api.deepseek.com/chat/completions"
DEEPSEEK_API_URL_REASONER = "https://api.deepseek.com/generate-reasoner"
#DEEPSEEK_API_KEY = os.getenv("sk-cb181ffbe7f5431289be60707a0a388b")
#OPENAI_API_KEY = os.getenv("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")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") # Todo Prod : créer les variables d'environnement
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"  # Peut être remplacé par "gpt-3.5-turbo" si besoin

# Configuration du client OpenAI (pour OpenAI et DeepSeek)
deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# def analyze_text_with_ai(text, document_type):
#     """Analyse un document avec DeepSeek AI (deepseek-chat), et bascule vers OpenAI en cas d'échec."""
#     print('::::text', text)
    
#     # Sélection du prompt en fonction du type de document
#     if document_type == "letter":
#         prompt = f"Analyse cette lettre de motivation et donne un avis détaillé avec des suggestions d'amélioration :\n{text}"
#     elif document_type == "bulletin":
#         prompt = ("Voici les données de relevés de notes (bulletin) provenant de Google Cloud Vision. "
#                   "Extrait les informations clés et retourne un JSON structuré contenant :\n"
#                   "- Nom de l'étudiant\n"
#                   "- Établissement\n"
#                   "- Année académique\n"
#                   "- Liste des matières avec leurs notes\n"
#                   "Si certaines informations sont manquantes, ignore-les.")
#     elif document_type == "cv":
#         prompt = ("Donne une analyse très efficace du CV en mettant en avant :\n"
#                   "- Les points forts\n"
#                   "- Les points faibles\n"
#                   "- Les axes d'amélioration\n"
#                   "Par ailleurs, extrait les informations clés et retourne un JSON structuré avec :\n"
#                   "- Nom et prénom\n"
#                   "- Expérience professionnelle\n"
#                   "- Compétences\n"
#                   "- Diplômes et formations\n"
#                   "- Certifications (si disponibles)")
#     else:
#         return {"error": "Type de document non pris en charge"}
    
#     # 🔹 Tentative d'utilisation de DeepSeek AI
#     try:
#         response = deepseek_client.chat.completions.create(
#             model="deepseek-chat",
#             messages=[{"role": "system", "content": "Tu es un expert en analyse de documents académiques."},
#                       {"role": "user", "content": prompt}],
#             stream=False
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         print(f"⚠️ DeepSeek indisponible : {e}")
    
#     # 🔄 Basculer vers OpenAI si DeepSeek échoue
#     print("🔄 Basculage vers OpenAI...")
#     return analyze_text_with_openai(text, document_type)

def analyze_text_with_openai(text, document_type):
    """Analyse un document avec OpenAI GPT en fallback."""
    #print(':::::: ', text)
    # Sélection du prompt en fonction du type de document
    if document_type == "letter":
        prompt = f"Analyse cette lettre de motivation et donne un avis détaillé avec des suggestions d'amélioration :\n{text}"
    elif document_type == "bulletin":
        prompt = f"""Tu es un expert en équivalences de diplômes internationaux.
                    INSTRUCTIONS STRICTES :
                    1. Vérifie si le document est un relevé de notes valide
                    2. Si non valide → Réponds uniquement "Bulletin non conforme"
                    3. Si valide → Convertis UNIQUEMENT les éléments suivants vers le système français :
                    - Notes : conversion sur 20
                    - Matières : traduction exacte en français
                    - Appréciations : traduction en français

                    FORMAT DE RÉPONSE (JSON strict) :
                    {{
                        "lastname": "nom de l'étudiant",
                        "firstname": "prenom de l'étudiant",
                        "school_name": "nom de l'établissement",
                        "academic_year": "année académique",
                        "subject": [
                            {{
                                "nom": "équivalence de la matière en français (France)",
                                "note": "note sur 20"
                                "weight": "Coefficient si applicable"
                            }}
                        ]
                    }}

                    RÈGLES IMPORTANTES :
                    - Ne pas ajouter d'informations non présentes dans le document original
                    - Ne pas créer d'appréciations ou de mentions si absentes
                    - Conserver uniquement les champs renseignés dans le document
                    - Pas de commentaires ou analyses supplémentaires

                    Données OCR à analyser :
                    {text}"""
    elif document_type == "cv":
        prompt = f"""Nous sommes en Février 2025. Tu es un expert en recrutement Campus France spécialisé dans l'évaluation des dossiers d'admission. 
                     Ta mission est d'analyser rigoureusement ce CV d'un candidat souhaitant continuer ces études en France. Le but est d'être le plus concret possible avec des exemples pris dans le cv.
                     N'analyse pas les compétences linguistiques (ex : niveau de langue, langues parlées). Ignore ces informations. 
                     Ne rajoute aucune phrase de conclusion ou d'encouragement. Limite ta réponse strictement aux sections demandées.
                     Analyse ce CV de manière détaillée en français:
  
                            1. Points forts 💪 (Identifier les Points forts uniquement en 2 phrases. Sois très concis ici, il faut des phrases très courtes)
                            - ✨ ...
                            - 🔥 ...

                            2. Points d'amélioration ⚠️ 
                            - 📝 Expressions et orthographes : Relève les phrases à améliorer avec corrections + suggestions 
 
                            - 🌟 Suggestions d'optimisation : Points critiques à renforcer pour le CV
                            ...
                            -  Rajoutes autant de point que tu peux sur tout autres remarques que tu jugeras important


                            3. Forme 🎨 
                            - Analyse uniquement la structure et la lisibilité du CV.  
                            - Si la forme est correcte, n’affiche rien sur cette section.  
                            - Si la forme présente des problèmes (ex: désordre, mauvaise lisibilité, incohérences graphiques, etc, etc), mentionne les points précis à améliorer.  

                            🎯 Conclusion: (faire le lien avec ces candidatures campus france)
                            - Avis global 
                            - Action prioritaire à faire
 
                            📊 Affiche à la fin le nombre de tokens utilisés : Entrée/Sortie

                            Tu dois donc analyser les metadata du CV extraite par "PDF Extract API", et donner un rapport très compréhensible à un étudiant (il faut tutoyer et créer un sentiment de confiance et de proximité avec lui).
                            metadata (PDF Extract API) du CV :
                            {text}"""
 
        prompt2 = f"""You are a Campus France recruitment expert specialized in evaluating admission applications. Your mission is to rigorously analyze this CV from a candidate wishing to continue their studies in France. Check if the metadata extracted from the CV contains elements relating to the following categories:
                - Education/studies: Bachelor's, Master's, High School Diploma...
                - Professional experience: Positions held, companies, employment periods...
                - Contact: Email, phone, address...
                - Skills: Software, technical or professional abilities...

                Do not reformulate or directly display contact information, education, professional experiences and skills. Use them only for analysis. CV sections may appear in `key_sections`, `section_headings` or `text_elements`. Be sure to check all three categories.

                If these minimal criteria are not met, only respond "CV non-compliant". If the CV is valid, analyze this CV in detail in english:

                1. Strengths 💪 (Identify Strengths only in 2 sentences. Be very concise here, sentences must be very short)
                - ✨ ...
                - 🔥 ...

                2. Areas for Improvement ⚠️
                - 📝 Expression and spelling: Note sentences to improve with corrections + suggestions
                - 🌟 Optimization suggestions: Critical points to strengthen for the CV...
                - Add as many points as you can on any other remarks you deem important

                3. Format 🎨
                - Analyze only the structure and readability of the CV
                - If the format is correct, display nothing for this section
                - If the format has problems (e.g.: disorder, poor readability, graphic inconsistencies, etc.), mention specific points to improve, but never give a grade

                🎯 Conclusion: (make the connection with these Campus France applications)
                - Constructive overall opinion
                - Priority action to take

                📊 Display at the end the number of tokens used: Input/Output

                You must therefore analyze the CV metadata extracted by "PDF Extract API", and give a very understandable report to a student (you must use informal "tu" and create a feeling of trust and closeness with them).

                CV metadata (PDF Extract API): {text}"""
 
    else:
        return {"error": "Type de document non pris en charge"}

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": "Tu es un expert en analyse de documents académiques."},
                      {"role": "user", "content": prompt}],
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return {"error": f"Erreur avec OpenAI : {e}"}

# llm_service.py (nouvelles fonctions)

def analyze_multiple_documents(documents_data, doc_type, cv_context=None):
    """Analyse plusieurs documents du même type en une seule fois"""
    
    if doc_type == "bulletin":
        prompt = f"""
        Tu es un expert en équivalences de diplômes internationaux et tu sais adapté tout bulletin au système français. Analyse les {len(documents_data)} bulletins de notes fournis en respectant scrupuleusement le format JSON demandé.
        ATTENTION: Ta réponse doit contenir UNIQUEMENT du JSON valide, sans aucun texte d'explication avant ou après. Ne pas inclure de commentaires ni d'explications.

        INSTRUCTIONS CLÉS
            1. Identification des éléments académiques:
                • Pour chaque matière, identifie précisément son nom, coefficient, note et rang (si disponible)
                • Les TP sont souvent indiqués par "TP", "Travaux Pratiques", "Practical Work", "Lab"
                • Le système de notation varie: /20, /100, A-F, 1-6 
            2. Détection du niveau d'études:
                • Lycée: Seconde, Première, Terminale (ou équivalents internationaux)
                • Supérieur: BAC+1 à BAC+8 (Licence = BAC+3, Master = BAC+5, Doctorat = BAC+8)
            3. Années académiques:
                • Année blanche: interruption d'études visible par un écart de plus d'un an entre années consécutives
                • Redoublement: souvent indiqué par "R", "Redoublant", "Repeat" ou années identiques consécutives
            4. Candidature Master:
                • Un candidat est éligible au master s'il a minimum BAC+4 AVEC une moyenne ≥ 14/20 (ou équivalent)
            5. Organisation des bulletins:
                • Lycée: généralement 3 trimestres par année
                • Supérieur: généralement 2 semestres par année
                • Les matières des trimestres/semestres doivent être regroupées ensemble dans un tableau [] et chaque matière doit avoir une réference : 1, 2, 3, etc. en fonction de l'ordre d'apparition
                • Le baccalauréat a souvent un relevé spécifique
                • Si les matières sont dans une autre langue, donne l'équivalence français tant que possible
            6. Redoublement / Année blanche
                • Un redoublement est souvent indiquée par "redoublement" ou "R" dans les bulletins de notes. N'hésites pas à trouver aussi d'autre
                • Pour le nombre d'année blanche, regardes l'écart entre les années d'études
            7. Inclus toutes les matières sans exception aucune dans l'ordre exact où elles apparaissent dans les bulletins

            
        INSTRUCTION ABSOLUE #1: Tu DOIS inclure TOUTES les matières présentes dans chaque bulletin, sans AUCUNE exception. Cette instruction est la plus importante de toutes.

        INSTRUCTION ABSOLUE #2: Ta réponse doit être UNIQUEMENT du JSON valide, sans aucun texte avant ou après.

        INSTRUCTION ABSOLUE #3: Tous les bulletins (reportCard1, reportCard2, reportCard3) doivent contenir TOUTES les matières visibles sur les images, même si cela signifie inclure 15+ matières par bulletin.
        Analyse les {len(documents_data)} bulletins de notes fournis en respectant ces instructions critiques.
        INSTRUCTION ABSOLUE: #4: tu DOIS traduire TOUTES les matières en FRANÇAIS.
        INSTRUCTION ABSOLUE: #5: Pour un report card donnée, renseigne tous les tableaux. Par exemple, si reportCart3 correspond à une année de lycée, et qu'uniquement le 1er trimestre est disponible, reportCard3 dois ressembler à ceci : [[matieres premier trimestre], [tableau vide car pas de 2eme trimestre], [tableau vide car pas de 3eme trimestre]]. Même analogie pour les années supérieures.
        INSTRUCTION ABSOLUE: #6: Fourni le nombre de tokens (input/output) utilisés à la fin de ta réponse.

        FORMAT DE RÉPONSE JSON
        {{
            "lastname": "NOM DE L'ÉTUDIANT",
            "firstname": "PRÉNOM DE L'ÉTUDIANT",
            "salutation": "Monsieur ou Madame",
            "nationality": "Nationalité la plus probable (ex: Camerounaise, Française)",
            "birthDate": {{
                "date": "jj/mm/aaaa"
            }},
            "phone": "TÉLÉPHONE si disponible",
            "phoneNumberFormatted": {{
                "name": "Numéro avec indicatif (ex: +237696073506 pour Cameroun)"
            }},
            "address": {{
                "name": "Adresse si disponible"
            }},
            "schoolLevelSelected": "Supérieur ou Lycée",
            "universityLevelSelected": {{
                "name": "BAC+X (1 à 8) ou null si lycéen"
            }},
            "selectedSchoolYear3": {{
                "name": "Année la plus récente (ex: 2024)"
            }},
            "degreeSelected": {{
                "name": "Niveau d'étude récent. Choisir uniquement dans cette liste ce qui convient le mieux au candidat : Seconde, Première (BAC-2), Terminale (BAC-1), BAC, BTS, DUT, CPGE, Licence, Master, Doctorat, Licence professionnelle, Diplôme d'ingénieur, Autre"
            }},
            "degreeExactNameValue": "Nom exact du diplôme récent (ex: Baccalauréat Scientifique, Licence en Informatique, Master en Génie Civil, Diplôme d'ingénieur en Génie Electrique, etc.)",
            "classRepetitionNumber": "Nombre de redoublements (0 si aucun)",
            "blankYearRepetitionNumber": "Nombre d'années blanches (0 si aucune)",
            "selectedCountry": {{
                "iso2": "Code pays (CM, FR, etc.)"
            }},
            "isFrancophoneCountry": true,
            "isFrancophone": true,
            "academicYearHeadDetails3": {{
                "city": {{
                    "name": "Ville de l'établissement en français"
                }},
                "country": {{
                    "name": "Pays de l'établissement en français"
                }},
                "markSystem": {{
                    "name": "Sur 6, Sur 10, Sur 20, Sur 100, ou Lettres (A+, A, B-, etc.)"
                }},
                "schoolName": "Nom de l'établissement",
                "spokenLanguage": "Langue d'enseignement en français"
            }},
            "applyingForMaster": true,
            "reportCard3": [
                [
                    {{
                        "reference": 1,
                        "label": {{
                            "value": "Nom matière ou du module (ex : Mathématiques, Physique, Anglais, etc.)"
                        }},
                        "weight": {{
                            "value": "Coefficient ou nombre de crédits"
                        }},
                        "mark": {{
                            "value": "Note suivant le système de notation défini dans academicYearHeadDetails3"
                        }},
                        "rank": {{
                            "value": "Rang si disponible"
                        }},
                        "isPracticalWork": true
                    }}
                    ...
                ]
                ...
                 /* TU DOIS INCLURE ICI ABSOLUMENT TOUTES LES MATIÈRES DU BULLETIN N, SANS EXCEPTION */
            ],
            "programDomainObj": {{
                "name": "Domaine d'étude (null si lycée)"
            }},
            "selectedSchoolYear2": {{ 
                "name": "Année précédente" 
            }},
            "academicYearHeadDetails2": {{ 
                "city": {{ "name": "Ville" }},
                "country": {{ "name": "Pays" }},
                "markSystem": {{ "name": "Système de notation" }},
                "schoolName": "Établissement",
                "spokenLanguage": "Langue d'enseignement"
            }},
            "reportCard2": [ 
            [ {{ "reference": 1, "label": {{ "value": "Matière" }}, "weight": {{ "value": "Coefficient" }}, "mark": {{ "value": "Note" }}, "rank": {{ "value": "Rang" }}, "isPracticalWork": false }} ] 
                ...
                 /* TU DOIS INCLURE ICI ABSOLUMENT TOUTES LES MATIÈRES DU BULLETIN N-1, SANS EXCEPTION */
            ],
            "selectedSchoolYear1": {{ 
                "name": "Année la plus ancienne" 
            }},
            "academicYearHeadDetails1": {{ 
                "city": {{ "name": "Ville" }},
                "country": {{ "name": "Pays" }},
                "markSystem": {{ "name": "Système de notation" }},
                "schoolName": "Établissement",
                "spokenLanguage": "Langue d'enseignement"
            }},
            "reportCard1": [ 
                [ {{ "reference": 1, "label": {{ "value": "Matière" }}, "weight": {{ "value": "Coefficient" }}, "mark": {{ "value": "Note" }}, "rank": {{ "value": "Rang" }}, "isPracticalWork": false }} ],
                 ...
                            /* TU DOIS INCLURE ICI ABSOLUMENT TOUTES LES MATIÈRES DU BULLETIN N-3, SANS EXCEPTION */

            ],
            "baccaulaureat": [
              [ {{ "reference": 1, "label": {{ "value": "Matière du BAC" }}, "weight": {{ "value": "Coefficient" }}, "mark": {{ "value": "Note" }}, "rank": {{ "value": "Rang" }}, "isPracticalWork": false, "isBaccalaureat": true }} ]
              [ {{ "reference": 2, "label": {{ "value": "Matière du BAC" }}, "weight": {{ "value": "Coefficient" }}, "mark": {{ "value": "Note" }}, "rank": {{ "value": "Rang" }}, "isPracticalWork": false, "isBaccalaureat": true }} ]
                ...
                 /* TU DOIS INCLURE ICI ABSOLUMENT TOUTES LES MATIÈRES DU baccaulaureat si c'est disponible, SANS EXCEPTION */
            ]
            "tokens": {{
                "input": "Nombre de tokens utilisés par le llm en entrée",
                "output": "Nombre de tokens utilisés par le llm  en sortie"
            }}  
        }}

        EXEMPLES D'IDENTIFICATION
            1. Systèmes de notation:
                • "14,5/20" ou "14.5 sur 20" → "Sur 20"
                • "87%" ou "87/100" → "Sur 100"
                • "A+", "B-" → "Lettres (A+, A, B-, etc.)"
                • "5,2" (Suisse) → "Sur 6"
            2. Niveaux d'étude et correspondances:
                • "L1", "S1+S2", "1ère année" → "BAC+1"
                • "L2", "2ème année" → "BAC+2"
                • "L3", "3ème année", "Licence" → "BAC+3"
                • "M1", "4ème année", "Maîtrise" → "BAC+4"
                • "M2", "5ème année", "Master" → "BAC+5"
                • "Grade 10" → "Seconde" (système américain)
                • "Grade 11" → "Première" (système américain)
                • "Grade 12" → "Terminale" (système américain)
            3. Domaines d'étude (traduction en français):
                • "Computer Science", "Informatique" → "Informatique"
                • "Civil Engineering", "Génie Civil" → "Génie Civil"
                • "Business Administration" → "Administration des Affaires"

        N'omets aucun champ, même si tu dois utiliser des valeurs par défaut cohérentes quand l'information n'est pas disponible.

        ATTENTION FINALE: Je répète, inclus ABSOLUMENT TOUTES les matières des bulletins sans aucune sélection ni tri. C'est CRUCIAL.
        📊 Affiche à la fin le nombre de tokens utilisés : Entrée/Sortie
        Bulletins à analyser :
        {json.dumps(documents_data, indent=2)}
        """
                    
    elif doc_type == "letter" and cv_context:
        prompt = f"""Tu es un expert Campus France spécialisé dans l'évaluation des dossiers d'admission.
                    Tu dois analyser {len(documents_data)} lettres de motivation en te basant sur le CV du candidat.
                    Tu dois tutoyer l'étudiant et créer un sentiment de confiance et de proximité.

                    Voici les informations extraites du CV que tu dois utiliser pour contextualiser ton analyse :
                    {cv_context}

                    Pour chaque lettre de motivation ({", ".join(documents_data.keys())}), analyse en détail les aspects suivants :

                    *1. Points forts 💪*
                    - Analyse la cohérence entre la formation demandée et le parcours académique/professionnel
                    - Vérifie la pertinence du choix de l'établissement
                    - Évalue la clarté et la cohérence du projet professionnel
                    
                    *2. Points d'amélioration ⚠️*
                    📝 *Améliorations à apporter dans la formulation :*
                    - Identifie les phrases à reformuler pour plus de clarté
                    - Propose des corrections pour chaque phrase problématique
                    - Format attendu pour chaque correction :
                      *Avant* → [phrase originale]
                      *Proposition* → [amélioration suggérée]

                    🌟 *Optimisations possibles :*
                    - Suggestions pour renforcer les liens entre expérience et formation visée
                    - Conseils pour mieux personnaliser le choix de l'établissement
                    - Recommandations pour améliorer la structure du projet professionnel

                    *🎯 Conclusion*
                    - *Avis global* : Synthèse constructive des forces et faiblesses
                    - *Actions prioritaires à faire* : Liste des 2-3 points d'amélioration les plus importants

                    INSTRUCTIONS IMPORTANTES:
                    1. Base ton analyse sur les critères prioritaires de Campus France :
                       - Justification du choix de la formation
                       - Justification du choix de l'établissement
                       - Clarté du projet professionnel post-formation
                    2. Sois précis dans tes suggestions d'amélioration avec des exemples concrets
                    3. Garde un ton constructif et encourageant
                    4. Utilise les emojis fournis pour la mise en forme
                    
                    📊 Affiche à la fin le nombre de tokens utilisés : Entrée/Sortie
                    Lettres à analyser :
                    {json.dumps(documents_data, indent=2)}"""

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un expert en analyse de documents académiques."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=6000  # Augmenté pour gérer plusieurs documents
        )
        return response.choices[0].message.content
    except Exception as e:
        return {"error": f"Erreur avec OpenAI : {e}"}
