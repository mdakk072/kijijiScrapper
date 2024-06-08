from typing import Dict
from core.coreDatabase.IDatabase import Database
from core.coreDatabase.SQLDatabase import SQLAlchemyDatabase
from core.coreDatabase.MongoDatabase import MongoDBDatabase

class DatabaseFactory:
    @staticmethod
    def create_database(db_type: str, connection_info: str, db_name: str, table_name: str, schema: Dict) -> Database:
        if db_type == 'SQL':
            return SQLAlchemyDatabase(connection_info, db_name, table_name, schema)
        elif db_type == 'mongodb':
            return MongoDBDatabase(connection_info, db_name, table_name, schema)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
