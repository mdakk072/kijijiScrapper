import json
from typing import Optional, Dict, Any

class ConfigICD:
    
    def __init__(self, 
                 name: Optional[str] = None, 
                 version: Optional[str] = None, 
                 log_path: Optional[str] = None, 
                 log_level: Optional[str] = None,
                 log_console: Optional[bool] = None,
                 log_file: Optional[bool] = None,
                 db_name: Optional[str] = None,
                 table_name: Optional[str] = None,
                 db_type: Optional[str] = None,
                 connection_info: Optional[str] = None,
                 do_pagination: Optional[bool] = None,
                 do_completion: Optional[bool] = None,
                 do_dead_link: Optional[bool] = None,
                 pagination: Optional[Dict[str, Any]] = None):
   
        self.name = name or "APP"
        self.version = version or "X.Y.Z.W"
        self.log_path = log_path or "data/log/app_log.log"
        self.log_level = log_level or "INFO"
        self.log_console = log_console if log_console is not None else False
        self.log_file = log_file if log_file is not None else True
        self.db_name = db_name 
        self.table_name = table_name 
        self.db_type = db_type 
        self.connection_info = connection_info 
        self.do_pagination = do_pagination if do_pagination is not None else False
        self.do_completion = do_completion if do_completion is not None else False
        self.do_dead_link = do_dead_link if do_dead_link is not None else False
        self.pagination = PaginationScrapperICD(**(pagination or {}))

    def parse(self, data: Dict[str, Any]) -> bool:
        """Parse a dictionary into the instance attributes."""
        self.name = data.get("name", self.name)
        self.version = data.get("version", self.version)
        self.log_path = data.get("log_path", self.log_path)
        self.log_level = data.get("log_level", self.log_level)
        self.log_console = data.get("log_console", self.log_console)
        self.log_file = data.get("log_file", self.log_file)
        self.db_name = data.get("db_name", self.db_name)
        self.table_name = data.get("table_name", self.table_name)
        self.db_type = data.get("db_type", self.db_type)
        self.connection_info = data.get("connection_info", self.connection_info)
        self.do_pagination = data.get("do_pagination", self.do_pagination)
        self.do_completion = data.get("do_completion", self.do_completion)
        self.do_dead_link = data.get("do_dead_link", self.do_dead_link)
        if self.pagination.parse(data.get("pagination", {})) is False:
            return False
        
        if not all([self.db_name, self.table_name, self.db_type, self.connection_info]):
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the instance to a dictionary and return a copy."""
        dict_ = self.__dict__.copy()
        dict_["pagination"] = self.pagination.to_dict()
        return dict_

    def to_json(self, indent: Optional[int] = None, ensure_ascii: bool = False) -> str:
        """Convert the instance to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii)      
      
    @staticmethod
    def metadata() -> Dict[str, Dict[str, Any]]:
        """Provide metadata for the ConfigICD fields."""
        return {
            "name": {
                "type": "string",
                "label": "Name",
                "description": "The name of the configuration."
            },
            "version": {
                "type": "string",
                "label": "Version",
                "description": "The version of the configuration."
            },
            "log_path": {
                "type": "string",
                "label": "Log Path",
                "description": "The path to the log file."
            },
            "log_level": {
                "type": "string",
                "label": "Log Level",
                "description": "The level of logging (e.g., DEBUG, INFO, WARNING, ERROR)."
            },
            "log_console": {
                "type": "bool",
                "label": "Log Console",
                "description": "Enable logging to console."
            },
            "log_file": {
                "type": "bool",
                "label": "Log File",
                "description": "Enable logging to file."
            },
            "db_name": {
                "type": "string",
                "label": "Database Name",
                "description": "The name of the database."
            },
            "table_name": {
                "type": "string",
                "label": "Table Name",
                "description": "The name of the table."
            },
            "db_type": {
                "type": "string",
                "label": "Database Type",
                "description": "The type of the database (e.g., SQL, MongoDB)."
            },
            "connection_info": {
                "type": "string",
                "label": "Connection Info",
                "description": "Connection information for the database."
            },
            "do_pagination": {
                "type": "bool",
                "label": "Do Pagination",
                "description": "Flag to enable pagination scraping."
            },
            "do_completion": {
                "type": "bool",
                "label": "Do Completion",
                "description": "Flag to enable completion scraping."
            },
            "do_dead_link": {
                "type": "bool",
                "label": "Do Dead Link",
                "description": "Flag to enable dead link scraping."
            },
            "pagination": PaginationScrapperICD.metadata()
        }

    @staticmethod
    def get_schema() -> Dict[str, Dict[str, Any]]:
        """Return a dictionary representing the configuration schema with attributes."""
        return {
            "name": {"type": "TEXT", "unique": True},
            "version": {"type": "TEXT"},
            "log_path": {"type": "TEXT", "default": "data/log/app_log.log"},
            "log_level": {"type": "TEXT", "default": "INFO"},
            "log_console": {"type": "INTEGER", "default": 0},
            "log_file": {"type": "INTEGER", "default": 1},
            "db_name": {"type": "TEXT", "default": "kijiji"},
            "table_name": {"type": "TEXT"},
            "db_type": {"type": "TEXT"},
            "connection_info": {"type": "TEXT"},
            "do_pagination": {"type": "INTEGER", "default": 0},
            "do_completion": {"type": "INTEGER", "default": 0},
            "do_dead_link": {"type": "INTEGER", "default": 0},
            **PaginationScrapperICD.get_schema()
        }

class PaginationScrapperICD:
    
    def __init__(self, 
                 base_url: Optional[str] = None, 
                 start_page: Optional[int] = None, 
                 max_zero_added: Optional[int] = None,
                 url_settings: Optional[Dict[str, Any]] = None):
   
        self.base_url = base_url or "https://www.kijiji.ca/b-{category}/levis/page-{start_page}/{category-id}?address={address}&ll={latitude},{longitude}&radius={radius}&ad=offer&sort={sort}"
        self.start_page = start_page or 1
        self.max_zero_added = max_zero_added or 2
        self.url_settings = url_settings or {
            "category": None,
            "category-id": None,
            "address": None,
            "latitude": None,
            "longitude":None,
            "radius": None,
            "sort": 'dateDesc'
        }

    def parse(self, data: Dict[str, Any]) -> bool:
        """Parse a dictionary into the instance attributes."""
        self.base_url = data.get("base_url", self.base_url)
        self.start_page = data.get("start_page", self.start_page)
        self.max_zero_added = data.get("max_zero_added", self.max_zero_added)
        self.url_settings = data.get("url_settings", self.url_settings)

        if not all(self.url_settings.get(key) for key in ["category", "category-id", "address"]):
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the instance to a dictionary and return a copy."""
        return self.__dict__.copy()

    def to_json(self, indent: Optional[int] = None, ensure_ascii: bool = False) -> str:
        """Convert the instance to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii)

    @staticmethod
    def metadata() -> Dict[str, Dict[str, Any]]:
        """Provide metadata for the PaginationScrapperICD fields."""
        return {
            "base_url": {
                "type": "string",
                "label": "Base URL",
                "description": "The base URL for pagination."
            },
            "start_page": {
                "type": "int",
                "label": "Start Page",
                "description": "The starting page number."
            },
            "max_zero_added": {
                "type": "int",
                "label": "Max Zero Added",
                "description": "Maximum number of zero added pages."
            },
            "url_settings": {
                "type": "dict",
                "label": "URL Settings",
                "description": "Settings for the URL.",
                "schema": {
                    "category": {"type": "string", "label": "Category", "description": "Category of the items."},
                    "category-id": {"type": "string", "label": "Category ID", "description": "ID of the category."},
                    "address": {"type": "string", "label": "Address", "description": "Address for the search."},
                    "latitude": {"type": "string", "label": "Latitude", "description": "Latitude coordinate."},
                    "longitude": {"type": "string", "label": "Longitude", "description": "Longitude coordinate."},
                    "radius": {"type": "string", "label": "Radius", "description": "Search radius."},
                    "sort": {"type": "string", "label": "Sort Order", "description": "Sorting order of the search results."}
                }
            }
        }

    @staticmethod
    def get_schema() -> Dict[str, Dict[str, Any]]:
        """Return a dictionary representing the configuration schema with attributes."""
        return {
            "base_url": {"type": "TEXT", "default": "https://www.kijiji.ca/b-{category}/levis/page-{start_page}/{category-id}?address={address}&ll={latitude},{longitude}&radius={radius}&ad=offer&sort={sort}"},
            "start_page": {"type": "INTEGER", "default": 1},
            "max_zero_added": {"type": "INTEGER", "default": 2},
            "url_settings": {
                "type": "DICT", 
                "default": {
                    "category":None,
                    "category-id":None,
                    "address": None,
                    "latitude": None,
                    "longitude": None,
                    "radius": '1.0',
                    "sort": 'dateDesc'
                }
            }
        }
