"""
Appwrite service for storage and database operations.
"""
from appwrite.client import Client
from appwrite.services.storage import Storage
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.input_file import InputFile
import config
import os

class AppwriteService:
    """Handles interactions with Appwrite."""
    
    def __init__(self):
        self.client = Client()
        self.client.set_endpoint(config.APPWRITE_ENDPOINT)
        self.client.set_project(config.APPWRITE_PROJECT_ID)
        self.client.set_key(config.APPWRITE_API_KEY)
        
        self.storage = Storage(self.client)
        self.databases = Databases(self.client)
        
        self._ensure_resources_exist()
    
    def _ensure_resources_exist(self):
        """Ensure database, collections, and bucket exist."""
        try:
            # 1. Check/Create Database
            try:
                self.databases.get(config.APPWRITE_DATABASE_ID)
            except:
                print(f"Creating Appwrite Database: {config.APPWRITE_DATABASE_ID}")
                self.databases.create(config.APPWRITE_DATABASE_ID, "Chat Database")

            # 2. Check/Create Collections & Attributes
            self._ensure_collection(
                config.APPWRITE_COLLECTION_ID, 
                "Chat History",
                [
                    {"key": "session_id", "type": "string", "size": 255, "required": True},
                    {"key": "message_type", "type": "string", "size": 50, "required": True},
                    {"key": "content", "type": "string", "size": 10000, "required": True},
                    {"key": "metadata", "type": "string", "size": 10000, "required": False},
                    {"key": "timestamp", "type": "datetime", "required": False}, # Appwrite handles creation time, but we might want explicit
                ]
            )
            
            self._ensure_collection(
                "sessions", 
                "Chat Sessions",
                [
                    {"key": "name", "type": "string", "size": 255, "required": True},
                    {"key": "mode", "type": "string", "size": 50, "required": True},
                    {"key": "pdf_id", "type": "string", "size": 255, "required": False},
                    {"key": "created_at", "type": "datetime", "required": False},
                    {"key": "updated_at", "type": "datetime", "required": False},
                ]
            )

            # 3. Check/Create Storage Bucket
            try:
                self.storage.get_bucket(config.APPWRITE_BUCKET_ID)
            except:
                print(f"Creating Appwrite Bucket: {config.APPWRITE_BUCKET_ID}")
                self.storage.create_bucket(
                    bucket_id=config.APPWRITE_BUCKET_ID,
                    name="PDF Storage",
                    permissions=["role:all"], # Public read? Or restricted? Let's keep default private for now
                    file_security=False,
                    enabled=True,
                    encryption=True,
                    antivirus=True
                )
                
        except Exception as e:
            print(f"Error initializing Appwrite resources: {e}")

    def _ensure_collection(self, collection_id, name, attributes):
        """Helper to ensure a collection and its attributes exist."""
        try:
            self.databases.get_collection(config.APPWRITE_DATABASE_ID, collection_id)
        except:
            print(f"Creating Collection: {name} ({collection_id})")
            self.databases.create_collection(
                database_id=config.APPWRITE_DATABASE_ID,
                collection_id=collection_id,
                name=name
            )
            
        # Check/Create Attributes
        # Note: This is a simplified check. In prod, you'd check each attribute existence.
        # Here we just try to create them and ignore "already exists" errors.
        for attr in attributes:
            try:
                if attr['type'] == 'string':
                    self.databases.create_string_attribute(
                        database_id=config.APPWRITE_DATABASE_ID,
                        collection_id=collection_id,
                        key=attr['key'],
                        size=attr.get('size', 255),
                        required=attr['required']
                    )
                elif attr['type'] == 'datetime':
                    self.databases.create_datetime_attribute(
                        database_id=config.APPWRITE_DATABASE_ID,
                        collection_id=collection_id,
                        key=attr['key'],
                        required=attr['required']
                    )
                # Add other types if needed
            except Exception as e:
                # Attribute likely already exists
                pass

    def upload_file(self, file_content: bytes, filename: str) -> str:
        """
        Upload a file to Appwrite Storage.
        Returns the file ID.
        """
        try:
            # Create a temporary file to upload
            # Appwrite SDK expects a file-like object or path
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as temp:
                temp.write(file_content)
                temp_path = temp.name
            
            result = self.storage.create_file(
                bucket_id=config.APPWRITE_BUCKET_ID,
                file_id=ID.unique(),
                file=InputFile.from_path(temp_path, filename=filename)
            )
            
            os.unlink(temp_path) # Clean up temp file
            return result['$id']
        except Exception as e:
            print(f"Error uploading to Appwrite: {e}")
            # Fallback to local/tmp storage if Appwrite fails or not configured
            return None

    def save_chat_message(self, session_id: str, role: str, content: str):
        """Save a chat message to Appwrite Database."""
        try:
            self.databases.create_document(
                database_id=config.APPWRITE_DATABASE_ID,
                collection_id=config.APPWRITE_COLLECTION_ID,
                document_id=ID.unique(),
                data={
                    "session_id": session_id,
                    "role": role,
                    "content": content,
                    "timestamp": "now()" # Appwrite handles datetime
                }
            )
        except Exception as e:
            print(f"Error saving message to Appwrite: {e}")

# Singleton
_appwrite_service = None

def get_appwrite_service():
    global _appwrite_service
    if _appwrite_service is None:
        if config.APPWRITE_PROJECT_ID and config.APPWRITE_API_KEY:
            _appwrite_service = AppwriteService()
    return _appwrite_service
