import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from common.services.document_extraction_service import extract_text_google_vision, extract_text_from_pdf, extract_text_from_adobe_pdf_extractor
from common.services.llm_service import analyze_text_with_openai, analyze_multiple_documents
from googleapiclient.http import MediaIoBaseDownload

UPLOAD_FOLDER = "uploads" 
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def init_routes(app):
    @app.route("/api/upload", methods=["POST"])
    def upload_file():
        """Upload le fichier et retourne son URL pour analyse"""
        if "file" not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Fichier non sélectionné"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            #file_path = f"http://127.0.0.1:5000/uploads/{filename}"
            return jsonify({"message": "Fichier uploadé avec succès", "file_path": file_path})

        return jsonify({"error": "Format de fichier non supporté"}), 400

    @app.route("/api/analyze-from-url", methods=["POST"])
    def analyze_from_url():
        """Analyse un fichier à partir de son URL"""
        data = request.json
        file_path = data.get("file_path")

        if not file_path:
            return jsonify({"error": "Aucune URL fournie"}), 400

        file_path = os.path.join(UPLOAD_FOLDER, os.path.basename(file_path))
        if not os.path.exists(file_path):
            return jsonify({"error": "Fichier introuvable"}), 404

        # 📌 Si PDF, extraire le texte
        if file_path.endswith(".pdf"):
            #extracted_text = extract_text_from_pdf(file_path)
            extracted_text = extract_text_from_adobe_pdf_extractor(file_path)
        else:
            extracted_text = extract_text_google_vision(file_path)

        # 🔹 Analyse IA
        document_type = "letter" if "motivation" in file_path.lower() else "bulletin" if "bulletin" in file_path.lower() else "cv"
        analysis = analyze_text_with_openai(extracted_text, 'cv')
        

        return jsonify({"extracted_text": extracted_text, "analysis": analysis})

    # document_extraction_route.py (nouveau endpoint)

# document_extraction_route.py (nouveau endpoint)

    @app.route("/api/analyze-multiple", methods=["POST"])
    def analyze_multiple_files():
        """Analyse plusieurs fichiers selon le focus demandé"""
        data = request.json
        
        if not data:
            return jsonify({"error": "Aucune donnée fournie"}), 400

        analyse_focus = data.get("analyse_focus")
        if not analyse_focus or analyse_focus not in ["bulletin", "letter"]:
            return jsonify({"error": "analyse_focus invalide"}), 400
        
        # Vérifier si on traite des fichiers Drive
        direct_from_drive = data.get("direct_from_drive", False)

        results = {}
        
        # Analyse des bulletins
        if analyse_focus == "bulletin":
            bulletin_paths = data.get("bulletin_paths", {})
            if not bulletin_paths:
                return jsonify({"error": "Aucun bulletin fourni"}), 400
                
            # Extraction et préparation des données de tous les bulletins
            bulletins_data = {}
            
            for bulletin_type, path_or_id in bulletin_paths.items():
                if direct_from_drive:
                    # Télécharger le fichier depuis Google Drive
                    try:
                        # Récupérer les métadonnées pour déterminer le type
                        from common.routes.google_drive_api_route import get_drive_service
                        drive_service = get_drive_service() 
                        file_metadata = drive_service.files().get(fileId=path_or_id, fields="name, mimeType").execute()
                        mime_type = file_metadata.get('mimeType', '')
                        file_name = file_metadata.get('name', f"temp_{bulletin_type}")
                        
                        # Créer un nom de fichier temporaire
                        temp_filename = f"temp_{bulletin_type}_{path_or_id}"
                        temp_file_path = os.path.join(UPLOAD_FOLDER, temp_filename)
                        
                        # Vérifier si c'est un fichier Google Docs/Sheets/Slides
                        google_docs_mime_types = [
                            'application/vnd.google-apps.document',
                            'application/vnd.google-apps.spreadsheet',
                            'application/vnd.google-apps.presentation'
                        ]
                        
                        if mime_type in google_docs_mime_types:
                            # Déterminer le format d'export
                            export_mime_type = 'application/pdf'  # Exporter en PDF par défaut
                            
                            # Télécharger avec export
                            drive_request = drive_service.files().export_media(fileId=path_or_id, mimeType=export_mime_type)
                            temp_file_path += '.pdf'  # Ajouter l'extension
                        else:
                            # Télécharger normalement
                            drive_request = drive_service.files().get_media(fileId=path_or_id)
                            
                            # Ajouter l'extension appropriée
                            if 'jpeg' in mime_type.lower() or 'jpg' in mime_type.lower():
                                temp_file_path += '.jpg'
                            elif 'png' in mime_type.lower():
                                temp_file_path += '.png'
                            elif 'pdf' in mime_type.lower():
                                temp_file_path += '.pdf'
                        
                        # Télécharger le contenu
                        with open(temp_file_path, 'wb') as f:
                            downloader = MediaIoBaseDownload(f, drive_request)
                            done = False
                            while done is False:
                                status, done = downloader.next_chunk()
                        
                        file_path = temp_file_path
                        
                    except Exception as e:
                        return jsonify({"error": f"Erreur lors du téléchargement du fichier Drive: {str(e)}"}), 500
                else:
                    # Méthode originale avec chemins locaux
                    file_path = os.path.join(UPLOAD_FOLDER, os.path.basename(path_or_id))
                    if not os.path.exists(file_path):
                        return jsonify({"error": f"Fichier introuvable: {bulletin_type}"}), 404
                
                # Extraction du texte selon le type de fichier
                is_pdf = file_path.lower().endswith('.pdf')
                
                try:
                    if is_pdf:
                        # Utiliser l'extracteur PDF
                        extracted_text = extract_text_from_pdf(file_path)
                    else:
                        # Utiliser Google Vision pour les images
                        extracted_text = extract_text_google_vision(file_path)
                    
                    # Stocker le texte extrait
                    bulletins_data[bulletin_type] = extracted_text
                    
                    # Log pour debug
                    print(f"Extraction réussie pour {bulletin_type}, longueur du texte: {len(extracted_text)}")
                    
                except Exception as e:
                    return jsonify({"error": f"Erreur d'extraction pour {bulletin_type}: {str(e)}"}), 500
                
                # Supprimer le fichier temporaire si nécessaire
                if direct_from_drive and os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                    except Exception as e:
                        print(f"Attention: Échec de suppression du fichier temporaire {temp_file_path}: {str(e)}")
                        
            # Analyse groupée des bulletins
            results["bulletins_analysis"] = analyze_multiple_documents(
                bulletins_data, 
                "bulletin",
                None
            )
            # Print results for debugging
            print('bulletins_analysis 🥳', results["bulletins_analysis"])

        # Analyse des lettres
        elif analyse_focus == "letter":
            letter_paths = data.get("letter_paths", {})
            cv_path = data.get("cv_path")
            
            if not letter_paths or not cv_path:
                return jsonify({"error": "Lettres ou CV manquant"}), 400
                
            # Extraction du CV d'abord
            cv_filename = os.path.basename(cv_path)
            cv_file_path = os.path.join(UPLOAD_FOLDER, "CV", cv_filename)
            if not os.path.exists(cv_file_path):
                cv_file_path = os.path.join(UPLOAD_FOLDER, cv_filename)
                if not os.path.exists(cv_file_path):
                    secure_name = secure_filename(cv_filename)
                    cv_file_path = os.path.join(UPLOAD_FOLDER, "cv", secure_name)
                    if not os.path.exists(cv_file_path):
                        return jsonify({"error": f"CV introuvable. Chemins testés: uploads/CV/{cv_filename}, uploads/{cv_filename}, uploads/CV/{secure_name}"}), 404
                
            cv_text = extract_text_from_pdf(cv_file_path)  
                     
            # Extraction et analyse des lettres
            letters_data = {}
            for letter_id, filename in letter_paths.items():
                # Chercher d'abord dans le dossier uploads/Letter/
                file_path = os.path.join(UPLOAD_FOLDER, "letter", filename)
                if not os.path.exists(file_path):
                    # Si non trouvé, essayer directement dans uploads/
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    if not os.path.exists(file_path):
                        # Si toujours pas trouvé, essayer avec secure_filename
                        secure_name = secure_filename(filename)
                        file_path = os.path.join(UPLOAD_FOLDER, "Letter", secure_name)
                        if not os.path.exists(file_path):
                            return jsonify({"error": f"Lettre introuvable: {letter_id}. Chemins testés: uploads/Letter/{filename}, uploads/{filename}, uploads/Letter/{secure_name}"}), 404
                    
                extracted_text = extract_text_from_pdf(file_path)
                letters_data[letter_id] = extracted_text
                
            # Analyse des lettres avec le contexte du CV
            results["letters_analysis"] = analyze_multiple_documents(
                letters_data,
                "letter",
                cv_text
            )

        return jsonify(results)
