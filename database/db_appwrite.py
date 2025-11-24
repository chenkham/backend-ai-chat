"""
Appwrite database implementation for chat history.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from appwrite.query import Query
from services.appwrite_service import get_appwrite_service
import config

class AppwriteChatDatabase:
    """Manages Appwrite database for chat history."""
    
    def __init__(self):
        self.appwrite = get_appwrite_service()
        if not self.appwrite:
            raise Exception("Appwrite service not initialized")
            
        self.db_id = config.APPWRITE_DATABASE_ID
        self.collection_id = config.APPWRITE_COLLECTION_ID
        self.sessions_collection_id = "sessions" # We need a separate collection for sessions
    
    def init_database(self):
        """Appwrite resources are assumed to exist or created via console."""
        pass
    
    def save_message(
        self, 
        session_id: str, 
        message_type: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save a chat message to Appwrite."""
        from appwrite.id import ID
        
        # Appwrite might prefer empty string over None for optional string attributes
        metadata_json = json.dumps(metadata) if metadata else "{}"
        
        try:
            result = self.appwrite.databases.create_document(
                database_id=self.db_id,
                collection_id=self.collection_id,
                document_id=ID.unique(),
                data={
                    "session_id": session_id,
                    "message_type": message_type,
                    "content": content,
                    "metadata": metadata_json,
                    "timestamp": datetime.now().isoformat()
                }
            )
            return result['$id']
        except Exception as e:
            print(f"❌ Error saving message to Appwrite: {e}")
            raise e
    
    def get_chat_history(
        self, 
        session_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve chat history from Appwrite."""
        queries = [Query.order_asc("timestamp")]
        
        if session_id:
            queries.append(Query.equal("session_id", session_id))
            
        if limit:
            queries.append(Query.limit(limit))
            
        result = self.appwrite.databases.list_documents(
            database_id=self.db_id,
            collection_id=self.collection_id,
            queries=queries
        )
        
        messages = []
        for doc in result['documents']:
            metadata = json.loads(doc['metadata']) if doc.get('metadata') else None
            messages.append({
                'id': doc['$id'],
                'session_id': doc['session_id'],
                'message_type': doc['message_type'],
                'content': doc['content'],
                'timestamp': doc['timestamp'],
                'metadata': metadata
            })
            
        return messages

    def create_session(
        self,
        session_id: str,
        name: str,
        mode: str,
        pdf_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new chat session in Appwrite."""
        now = datetime.now().isoformat()
        
        self.appwrite.databases.create_document(
            database_id=self.db_id,
            collection_id=self.sessions_collection_id,
            document_id=session_id, # Use session_id as document ID
            data={
                "name": name,
                "mode": mode,
                "pdf_id": pdf_id,
                "created_at": now,
                "updated_at": now
            }
        )
        
        return {
            'id': session_id,
            'name': name,
            'mode': mode,
            'pdf_id': pdf_id,
            'created_at': now,
            'updated_at': now
        }

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all chat sessions."""
        result = self.appwrite.databases.list_documents(
            database_id=self.db_id,
            collection_id=self.sessions_collection_id,
            queries=[Query.order_desc("updated_at")]
        )
        
        sessions = []
        for doc in result['documents']:
            sessions.append({
                'id': doc['$id'],
                'name': doc['name'],
                'mode': doc['mode'],
                'pdf_id': doc.get('pdf_id'),
                'created_at': doc['created_at'],
                'updated_at': doc['updated_at']
            })
        return sessions

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific session."""
        try:
            doc = self.appwrite.databases.get_document(
                database_id=self.db_id,
                collection_id=self.sessions_collection_id,
                document_id=session_id
            )
            return {
                'id': doc['$id'],
                'name': doc['name'],
                'mode': doc['mode'],
                'pdf_id': doc.get('pdf_id'),
                'created_at': doc['created_at'],
                'updated_at': doc['updated_at']
            }
        except:
            return None

    def delete_session_and_messages(self, session_id: str) -> bool:
        """Delete a session and all its messages."""
        try:
            # Delete session
            self.appwrite.databases.delete_document(
                database_id=self.db_id,
                collection_id=self.sessions_collection_id,
                document_id=session_id
            )
            
            # Delete messages (this might be slow if many messages, ideally use backend function)
            # For now, we'll list and delete
            messages = self.get_chat_history(session_id)
            for msg in messages:
                self.appwrite.databases.delete_document(
                    database_id=self.db_id,
                    collection_id=self.collection_id,
                    document_id=msg['id']
                )
            return True
        except:
            return False

    def update_session_timestamp(self, session_id: str):
        """Update session timestamp."""
        try:
            self.appwrite.databases.update_document(
                database_id=self.db_id,
                collection_id=self.sessions_collection_id,
                document_id=session_id,
                data={"updated_at": datetime.now().isoformat()}
            )
        except:
            pass
