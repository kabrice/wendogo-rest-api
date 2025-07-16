import os
import io
import json
import requests
import logging
import zipfile
from google.cloud import vision
from pdf2image import convert_from_path
from datetime import datetime
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult

# Configuration des logs
logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
 
# Configuration des logs
logging.basicConfig(level=logging.INFO)

# Définition du chemin de configuration des credentials Adobe
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
CONFIG_PATH = os.path.join(BASE_DIR, "config/pdfservices-api-credentials.json")

# Vérification de l'existence du fichier de configuration
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"❌ Le fichier de configuration Adobe est introuvable : {CONFIG_PATH}")

with open(CONFIG_PATH) as f:
    adobe_config = json.load(f)

API_KEY = adobe_config["client_credentials"]["client_id"]
EXTRACT_URL = "https://cpf-ue1.adobe.io/ops/:create?respondWith=%7B%22relationType%22%3A%22http%3A%2F%2Fns.adobe.com%2Fpdf%2Frel%2Fextract%22%7D"


def extract_text_google_vision(image_path):
    """Utilise Google Cloud Vision API pour extraire du texte d'une image"""
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(f"Erreur API : {response.error.message}")

    extracted_text = response.text_annotations[0].description if response.text_annotations else "Aucun texte détecté."
    return extracted_text

def extract_text_from_pdf(pdf_path):
    """Convertit un PDF en images, puis extrait le texte avec Google Vision API"""
    images = convert_from_path(pdf_path)
    full_text = ""

    for i, image in enumerate(images):
        temp_image_path = os.path.join(UPLOAD_FOLDER, f"temp_page_{i}.jpg")
        image.save(temp_image_path, "JPEG")  # Sauvegarde en fichier image
        
        text = extract_text_google_vision(temp_image_path)  # Exécute l'OCR
        full_text += text + "\n\n"

        os.remove(temp_image_path)  # Supprime l'image temporaire après OCR

    return full_text 

def analyze_pdf_structure(metadata):
    """Optimise les métadonnées PDF pour l'analyse de structure"""
    
    optimized = {
        "fonts": {},
        "text_elements": [],
        "layout_stats": {
            "font_sizes": {},
            "alignments": {},
            "colors": {},
            "line_spacing": {}
        }
    }

    # Détection des éléments clés
    key_sections = set()
    section_headings = []

    for element in metadata.get("elements", []):
        # Extraction des propriétés de texte
        if "Text" in element:
            text_entry = {
                "text": element["Text"],
                "font": {
                    "family": element.get("Font", {}).get("family_name"),
                    "weight": element.get("Font", {}).get("weight"),
                    "size": element.get("TextSize")
                },
                "alignment": element.get("attributes", {}).get("TextAlign"),
                "position": element.get("Bounds"),
                "language": element.get("Lang")
            }

            # Détection des titres de section
            if element.get("Path", "").split("/")[-1] in ["H1", "H2", "Title"]:
                section_headings.append(element["Text"])
                key_sections.add(element["Text"].strip().lower())

            optimized["text_elements"].append(text_entry)

            # Statistiques globales
            font_key = f"{text_entry['font']['family']}_{text_entry['font']['weight']}"
            optimized["fonts"][font_key] = text_entry["font"]

            optimized["layout_stats"]["font_sizes"][text_entry["font"]["size"]] = \
                optimized["layout_stats"]["font_sizes"].get(text_entry["font"]["size"], 0) + 1

            if text_entry["alignment"]:
                optimized["layout_stats"]["alignments"][text_entry["alignment"]] = \
                    optimized["layout_stats"]["alignments"].get(text_entry["alignment"], 0) + 1

    # Ajout des métadonnées étendues utiles
    optimized.update({
        "page_info": {
            "count": metadata.get("extended_metadata", {}).get("page_count"),
            "dimensions": metadata.get("pages", [{}])[0].get("boxes")
        },
        "key_sections": list(key_sections),
        "section_headings": section_headings
    })

    return optimized

def extract_text_from_adobe_pdf_extractor(pdf_path):
    try:
        credentials = ServicePrincipalCredentials(
            client_id=adobe_config["client_credentials"]["client_id"],
            client_secret=adobe_config["client_credentials"]["client_secret"]
        )
        
        pdf_services = PDFServices(credentials=credentials)
        
        with open(pdf_path, "rb") as pdf_file:
            input_stream = pdf_file.read()
        
        input_asset = pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.PDF)
        
        extract_pdf_params = ExtractPDFParams(
            elements_to_extract=[ExtractElementType.TEXT]
        )
        
        extract_pdf_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_pdf_params)
        location = pdf_services.submit(extract_pdf_job)
        pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)
        
        result_asset = pdf_services_response.get_result().get_resource()
        stream_asset = pdf_services.get_content(result_asset)
        
        output_file_path = create_output_file_path()
        with open(output_file_path, "wb") as file:
            file.write(stream_asset.get_input_stream())
        
        with zipfile.ZipFile(output_file_path, 'r') as archive:
            jsonentry = archive.open('structuredData.json')
            data = json.loads(jsonentry.read())
        #structured_data = analyze_pdf_structure(data)    
        return data

    except (ServiceApiException, ServiceUsageException, SdkException) as e:
        logging.exception(f"❌ Error extracting PDF: {e}")
        return {"error": str(e)}


def create_output_file_path() -> str:
    """Génère un chemin pour sauvegarder le fichier de sortie."""
    now = datetime.now()
    time_stamp = now.strftime("%Y-%m-%dT%H-%M-%S")
    output_dir = "output/ExtractTextInfoFromPDF"
    os.makedirs(output_dir, exist_ok=True)
    return f"{output_dir}/extract{time_stamp}.zip"
