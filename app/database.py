from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from app.config import settings
from typing import Optional


class DatabaseConnection:
    """Singleton class for managing MongoDB connections"""
    
    _instance: Optional["DatabaseConnection"] = None
    _client: Optional[MongoClient] = None
    _master_db: Optional[Database] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.connect()
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self._client = MongoClient(settings.MONGODB_URL)
            self._master_db = self._client[settings.MASTER_DB_NAME]
            # Test connection
            self._client.server_info()
            print(f"Connected to MongoDB: {settings.MONGODB_URL}")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise
    
    def get_master_db(self) -> Database:
        """Get the master database instance"""
        if self._master_db is None:
            self.connect()
        return self._master_db
    
    def get_collection(self, collection_name: str, database: Optional[Database] = None) -> Collection:
        """Get a collection from the database"""
        db = database or self._master_db
        return db[collection_name]
    
    def create_collection(self, collection_name: str, database: Optional[Database] = None):
        """Create a new collection in the database"""
        db = database or self._master_db
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"Created collection: {collection_name}")
        else:
            print(f"Collection already exists: {collection_name}")
    
    def drop_collection(self, collection_name: str, database: Optional[Database] = None):
        """Drop a collection from the database"""
        db = database or self._master_db
        if collection_name in db.list_collection_names():
            db.drop_collection(collection_name)
            print(f"Dropped collection: {collection_name}")
    
    def close(self):
        """Close the MongoDB connection"""
        if self._client:
            self._client.close()
            print("MongoDB connection closed")


# Singleton instance
db_connection = DatabaseConnection()
