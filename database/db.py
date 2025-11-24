"""
SQLite database initialization and management for chat history.
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import config


class ChatDatabase:
    """Manages SQLite database for chat history."""
    
    def __init__(self, db_path: Path = config.DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Chat history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                mode TEXT NOT NULL,
                pdf_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on session_id for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id 
            ON chat_history(session_id)
        """)
        
        conn.commit()
        conn.close()
    
    def save_message(
        self, 
        session_id: str, 
        message_type: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Save a chat message to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO chat_history (session_id, message_type, content, metadata)
            VALUES (?, ?, ?, ?)
        """, (session_id, message_type, content, metadata_json))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return message_id
    
    def get_chat_history(
        self, 
        session_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve chat history, optionally filtered by session_id."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if session_id:
            query = """
                SELECT * FROM chat_history 
                WHERE session_id = ? 
                ORDER BY timestamp ASC
            """
            params = (session_id,)
        else:
            query = """
                SELECT * FROM chat_history 
                ORDER BY timestamp DESC
            """
            params = ()
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            metadata = json.loads(row['metadata']) if row['metadata'] else None
            messages.append({
                'id': row['id'],
                'session_id': row['session_id'],
                'message_type': row['message_type'],
                'content': row['content'],
                'timestamp': row['timestamp'],
                'metadata': metadata
            })
        
        return messages
    
    def delete_session(self, session_id: str) -> int:
        """Delete all messages for a given session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM chat_history WHERE session_id = ?
        """, (session_id,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
    
    # Session Management
    
    def create_session(
        self,
        session_id: str,
        name: str,
        mode: str,
        pdf_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new chat session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        from datetime import datetime
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO sessions (id, name, mode, pdf_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, name, mode, pdf_id, now, now))
        
        conn.commit()
        conn.close()
        
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
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM sessions 
            ORDER BY updated_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            sessions.append({
                'id': row['id'],
                'name': row['name'],
                'mode': row['mode'],
                'pdf_id': row['pdf_id'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        return sessions
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific session by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM sessions WHERE id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'name': row['name'],
                'mode': row['mode'],
                'pdf_id': row['pdf_id'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        return None
    
    def delete_session_and_messages(self, session_id: str) -> bool:
        """Delete a session and all its messages."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete messages first
        cursor.execute("""
            DELETE FROM chat_history WHERE session_id = ?
        """, (session_id,))
        
        # Delete session
        cursor.execute("""
            DELETE FROM sessions WHERE id = ?
        """, (session_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    def update_session_timestamp(self, session_id: str):
        """Update the updated_at timestamp for a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        from datetime import datetime
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE sessions SET updated_at = ? WHERE id = ?
        """, (now, session_id))
        
        conn.commit()
        conn.close()


# Singleton instance
_db_instance = None


def get_database():
    """Get or create the database singleton instance."""
    global _db_instance
    if _db_instance is None:
        # Check if Appwrite is configured
        if config.APPWRITE_PROJECT_ID and config.APPWRITE_API_KEY:
            try:
                print("Attempting to initialize Appwrite Database...")
                from database.db_appwrite import AppwriteChatDatabase
                _db_instance = AppwriteChatDatabase()
                print("✅ Using Appwrite Database")
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"❌ Failed to initialize Appwrite Database: {e}. Falling back to SQLite.")
                _db_instance = ChatDatabase()
        else:
            _db_instance = ChatDatabase()
            print("Using SQLite Database")
            
    return _db_instance
