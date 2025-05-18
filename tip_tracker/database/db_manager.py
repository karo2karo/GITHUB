"""Database manager for MongoDB connection and configuration."""

from datetime import datetime
import pymongo
from pymongo import MongoClient
from config import MONGODB_URL, DATABASE_NAME, COLLECTIONS


class DatabaseManager:
    def __init__(self):
        """Initialize MongoDB connection and setup indexes."""
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        
        # Get collections
        self.tips_collection = self.db[COLLECTIONS['tips']]
        self.currencies_collection = self.db[COLLECTIONS['currencies']]
        self.settings_collection = self.db[COLLECTIONS['settings']]
        
        # Create indexes for faster queries
        self._create_indexes()
    
    def _create_indexes(self):
        """Create indexes for better query performance."""
        self.tips_collection.create_index([('date', pymongo.ASCENDING)])
        self.tips_collection.create_index([('currency', pymongo.ASCENDING)])
    
    def get_tips_collection(self):
        """Get the tips collection."""
        return self.tips_collection
    
    def get_currencies_collection(self):
        """Get the currencies collection."""
        return self.currencies_collection
    
    def get_settings_collection(self):
        """Get the settings collection."""
        return self.settings_collection
    
    def close_connection(self):
        """Close the MongoDB connection."""
        self.client.close()
    
    def test_connection(self, url, db_name):
        """Test connection to MongoDB with provided parameters."""
        try:
            test_client = MongoClient(url)
            test_db = test_client[db_name]
            # A simple operation to verify connection
            test_db.list_collection_names()
            return True, None
        except Exception as e:
            return False, str(e)