from flask import jsonify, request, make_response
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account 
from googleapiclient.http import MediaIoBaseDownload
import io
import io
import os
import json
import unicodedata
import re

# OAuth 2.0 configuration  

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "config/amiable-fin-googleserviceaccount.json")
FOLDER_ID = "1du7aT-YP2iN4zRWh2UZJcAbkp7yTn1tb" 

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
    return build('drive', 'v3', credentials=credentials)

# Disable SSL verification in development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
 

def init_routes(app):
    @app.route('/api/upload-to-drive', methods=['POST'])
    def upload_to_drive():
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'POST')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
        
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No file provided"}), 400

        file = request.files['file']
        user_id = request.form.get('user_id')  # Get user ID from frontend

        if not file or not file.filename:
            return jsonify({"success": False, "message": "No file selected"}), 400

        try:
            drive_service = get_drive_service()

            # Create or get user-specific folder
            user_folder_id = create_user_folder(drive_service, user_id)

            formatted_filename = remove_accents_and_special_chars(file.filename)

            prefix_mapping = {
                '0': 'BULLETIN_N_',
                '1': 'BULLETIN_N_1_',
                '2': 'BULLETIN_N_2_',
                '3': 'BACCALAUREAT_'
            }

            file_type_index = request.form.get('file_index', 'unknown')
            prefix = prefix_mapping.get(file_type_index, 'DOC_')

            file_metadata = {
                'name': f"{prefix}{formatted_filename}",
                'formatted_filename': f"{formatted_filename}",
                'parents': [user_folder_id]
            }


            media = MediaIoBaseUpload(
                io.BytesIO(file.read()),
                mimetype=file.content_type,
                resumable=True
            )

            uploaded_file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            print('😇file', file)
            
            return jsonify({
                "success": True,
                "file_id": uploaded_file.get('id'),
                "file_type_index": file_type_index,
                "name": formatted_filename               
            })
            # return jsonify({
            #     "success": True,
            #     "file_id": uploaded_file.get('id'),
            #     "name": formatted_filename,
            #     "url": uploaded_file.get('webViewLink')
            # })

        except Exception as e:
            print(f"Detailed error: {str(e)}")  # Add this line
            return jsonify({"success": False, "message": str(e)}), 500

    # Add a new route to init_routes function
    @app.route('/api/delete-from-drive', methods=['POST', 'OPTIONS'])
    def DELETED_from_drive():
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add('Access-Control-Allow-Origin',  request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'POST')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
        
        data = request.json
        file_id = data.get('file_id')
        
        if not file_id:
            return jsonify({"success": False, "message": "No file ID provided"}), 400
        
        try:
            drive_service = get_drive_service()
            
            # Get the current file metadata
            file = drive_service.files().get(fileId=file_id, fields='name').execute()
            current_name = file.get('name', '')
            
            # Add DELETED_ prefix if it's not already there
            if not current_name.startswith('DELETED_'):
                new_name = f"DELETED_{current_name}"
                
                # Update the file name
                drive_service.files().update(
                    fileId=file_id,
                    body={'name': new_name}
                ).execute()
            
            return jsonify({
                "success": True,
                "message": "File marked as deleted",
                "file_id": file_id
            })
        
        except Exception as e:
            print(f"Delete error: {str(e)}")
            return jsonify({"success": False, "message": str(e)}), 500  
                  
    @app.route('/api/preview-file/<file_id>', methods=['GET', 'OPTIONS'])
    def preview_file(file_id):
        # CORS headers handling
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
        
        try:
            drive_service = get_drive_service()
            
            # Get file metadata
            file_metadata = drive_service.files().get(fileId=file_id, fields='id, name, mimeType').execute()
            
            # Download the file content
            media_request = drive_service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, media_request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            file_content.seek(0)
            
            # Serve the file with proper content type
            response = make_response(file_content.read())
            response.headers.set('Content-Type', file_metadata.get('mimeType', 'application/octet-stream'))
            response.headers.set('Content-Disposition', f'inline; filename="{file_metadata.get("name")}"')
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            
            return response
        except Exception as e:
            print(f"Preview error: {str(e)}")
            response = jsonify({"success": False, "message": str(e)}), 500
            response[0].headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
            response[0].headers.add('Access-Control-Allow-Credentials', 'true')
            return response
        
def create_user_folder(drive_service, user_id):
    """
    Check if a folder exists for the user, otherwise create it.
    """
    query = f"name = '{user_id}' and mimeType = 'application/vnd.google-apps.folder' and '{FOLDER_ID}' in parents"
    results = drive_service.files().list(q=query, fields="files(id)").execute()
    folders = results.get('files', [])

    if folders:
        return folders[0]['id']  # Return existing folder ID

    # Create folder if it does not exist
    folder_metadata = {
        'name': str(user_id),
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [FOLDER_ID]
    }
    folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
    return folder.get('id')  # Return new folder ID

def remove_accents_and_special_chars(filename):
    """
    Remove accents and special characters from a filename.
    """
    filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)  # Replace special characters
    return filename




# Add this function to your Flask backend file

