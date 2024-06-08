from abc import ABC, abstractmethod
from typing import Dict, Any
from core.utils import Utils

class Database(ABC):
    def __init__(self, connection_info: str, db_name: str, table_name: str, schema: Dict = {}):
        self.connection_info = connection_info
        self.db_name = db_name
        self.table_name = table_name
        self.schema = schema
        self.logger = Utils.get_logger()
    
    @abstractmethod
    def initialize(self):
        """Perform additional initialization specific to the database."""
        pass

    @abstractmethod
    def connect(self):
        """Establish a database connection."""
        pass
    
    def disconnect(self):
        """Close the database connection."""
        pass

    @abstractmethod
    def create(self, data: Dict[str, Any]):
        """Create a new record in the database."""
        pass

    @abstractmethod
    def read(self, query: Dict[str, Any]) -> Any:
        """Read records from the database."""
        pass

    @abstractmethod
    def update(self, query: Dict[str, Any], data: Dict[str, Any]):
        """Update records in the database."""
        pass

    @abstractmethod
    def delete(self, query: Dict[str, Any]):
        """Delete records from the database."""
        pass

    @abstractmethod
    def define_table(self):
        """Define the table schema in the database."""
        pass
