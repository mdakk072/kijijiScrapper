from typing import Any, Dict
from pymongo import MongoClient, errors
from core.coreDatabase.IDatabase import Database

class MongoDBDatabase(Database):

    def initialize(self):
        self.connect()
        self.define_table()

    def connect(self):
        try:
            self.client = MongoClient(self.connection_info)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.table_name]
            self.logger.info("Database connection established.")
        except errors.ConnectionError as e:
            self.logger.error(f"Failed to connect to the database: {e}")
            raise

    def disconnect(self):
        self.client.close()

    def define_table(self):
        try:
            # Create indexes for unique fields
            for field, attrs in self.schema.items():
                if attrs.get("unique"):
                    self.collection.create_index([(field, 1)], unique=True)
            self.logger.info(f"Indexes for table '{self.table_name}' defined successfully.")
        except Exception as e:
            self.logger.error(f"Failed to define indexes for table '{self.table_name}': {e}")
            raise

    def create(self, data: Dict[str, Any]) -> bool:
        try:
            self.collection.insert_one(data)
            self.logger.info(f"Record created successfully: {data}")
            return True
        except errors.DuplicateKeyError:
            # Handle unique constraint violation without logging
            return False
        except Exception as e:
            self.logger.error(f"Failed to create record: {e}")
            return False
    
    def read(self, query: Dict[str, Any], limit: int = 0) -> Any:
        try:
            results = self.collection.find(query).limit(limit)
            self.logger.info(f"Records read successfully with query: {query}, limit: {limit}")
            return [doc for doc in results]
        except Exception as e:
            self.logger.error(f"Failed to read records with query: {e}")
            return []

    def update(self, query: Dict[str, Any], data: Dict[str, Any]) -> bool:
        try:
            self.collection.update_many(query, {'$set': data})
            return True
        except Exception as e:
            self.logger.error(f"Failed to update records with query: {e}")
            return False

    def delete(self, query: Dict[str, Any]) -> bool:
        try:
            self.collection.delete_many(query)
            self.logger.info(f"Records deleted successfully with query: {query}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete records with query: {e}")
            return False
