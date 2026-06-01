import sqlite3
import chromadb
from chromadb.utils import embedding_functions
import os
import datetime

class MemorySystem:
    def __init__(self, db_path="jarvis_memory.db"):
        self.db_path = db_path
        # Initialize Structured Memory (SQLite)
        self._init_sqlite()

        # Initialize Semantic Memory (ChromaDB)
        # Chroma runs in-process by default
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.chroma_client.get_or_create_collection(
            name="jarvis_conversations",
            embedding_function=self.embedding_fn
        )

    def _init_sqlite(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Table for user preferences, goals, and explicit facts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    value TEXT,
                    category TEXT,
                    updated_at TIMESTAMP
                )
            ''')
            conn.commit()

    # --- Structured Memory (Facts/Preferences) ---
    def save_fact(self, key, value, category="general"):
        """Saves a specific piece of information about the user or their world."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO facts (key, value, category, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (key, value, category, now))
            conn.commit()

    def get_fact(self, key):
        """Retrieves a specific fact by its key."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM facts WHERE key = ?', (key,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_all_facts(self):
        """Returns all stored facts as a dictionary."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT key, value FROM facts')
            return {row[0]: row[1] for row in cursor.fetchall()}

    # --- Semantic Memory (Conversations/Context) ---
    def add_conversation_memory(self, text, metadata=None):
        """Stores a piece of conversation in the vector database for semantic retrieval."""
        doc_id = f"msg_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {"timestamp": datetime.datetime.now().isoformat()}],
            ids=[doc_id]
        )

    def query_memory(self, query_text, n_results=3):
        """Retrieves the most relevant snippets from past conversations."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        # Chroma returns a list of lists
        return results['documents'][0] if results['documents'] else []

    def clear_semantic_memory(self):
        """Wipes the vector database."""
        self.collection.delete([]) # Delete all
