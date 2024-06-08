from datetime import datetime
import json
from typing import Optional, Dict, Any


class MonitoringICD:
    
    def __init__(self, 
                 id: Optional[str] = None,
                 state: Optional[str] = None,
                 start_time: Optional[str] = None, 
                 end_time: Optional[str] = None, 
                 duration: Optional[float] = None, 
                 status: Optional[str] = None, 
                 last_updated: Optional[str] = None,
                 num_requests: Optional[int] = None,
                 successful_requests: Optional[int] = None,
                 failed_requests: Optional[int] = None,
                 requests_per_minute: Optional[float] = None,
                 fault: Optional[bool] = None,
                 config: Optional[Dict[str, Any]] = None):
        
        self.id = id
        self.state = state 
        self.start_time = start_time if start_time else datetime.now().isoformat()
        self.end_time = end_time
        self.duration = duration
        self.status = status
        self.last_updated = last_updated
        self.num_requests = num_requests
        self.successful_requests = successful_requests
        self.failed_requests = failed_requests
        self.requests_per_minute = requests_per_minute
        self.fault = fault
        self.config = config
        
    def parse(self, data: Dict[str, Any]) -> bool:
        """Parse a dictionary into the instance attributes."""
        self.id = data.get("id", self.id)
        self.state = data.get("state", self.state)
        self.start_time = data.get("start_time", self.start_time)
        self.end_time = data.get("end_time", self.end_time)
        self.duration = data.get("duration", self.duration)
        self.status = data.get("status", self.status)
        self.last_updated = data.get("last_updated", self.last_updated)
        self.num_requests = data.get("num_requests", self.num_requests)
        self.successful_requests = data.get("successful_requests", self.successful_requests)
        self.failed_requests = data.get("failed_requests", self.failed_requests)
        self.requests_per_minute = data.get("requests_per_minute", self.requests_per_minute)
        self.fault = data.get("fault", self.fault)
        self.config = data.get("config", self.config)
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the instance to a dictionary and return a copy."""
        return self.__dict__.copy()

    def to_json(self, indent: Optional[int] = None, ensure_ascii: bool = False) -> str:
        """Convert the instance to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii)      
      
    @staticmethod
    def metadata() -> Dict[str, Dict[str, Any]]:
        """Provide metadata for the MonitoringICD fields."""
        return {
            "id": {
                "type": "string",
                "label": "ID",
                "description": "The unique identifier for the monitoring instance."
            },
            "state": {
                "type": "string",
                "label": "State",
                "description": "The current state of the monitoring instance."
            },
            "start_time": {
                "type": "string",
                "label": "Start Time",
                "description": "The timestamp when the scraper starts."
            },
            "end_time": {
                "type": "string",
                "label": "End Time",
                "description": "The timestamp when the scraper ends."
            },
            "duration": {
                "type": "float",
                "label": "Duration",
                "description": "Total execution time in seconds."
            },
            "status": {
                "type": "string",
                "label": "Status",
                "description": "Current status of the scraper (e.g., running, completed, paused)."
            },
            "last_updated": {
                "type": "string",
                "label": "Last Updated",
                "description": "Timestamp of the last status update."
            },
            "num_requests": {
                "type": "int",
                "label": "Number of Requests",
                "description": "Total number of HTTP requests made."
            },
            "successful_requests": {
                "type": "int",
                "label": "Successful Requests",
                "description": "Number of successful requests."
            },
            "failed_requests": {
                "type": "int",
                "label": "Failed Requests",
                "description": "Number of failed requests and their reasons."
            },
            "requests_per_minute": {
                "type": "float",
                "label": "Requests per Minute",
                "description": "Rate of requests over time."
            },
            "fault": {
                "type": "bool",
                "label": "Fault",
                "description": "Indicates if there was a fault during the scraping process."
            },
            "config": {
                "type": "dict",
                "label": "Configuration",
                "description": "The configuration used for the scraper run."
            }
        }

    @staticmethod
    def get_schema() -> Dict[str, Dict[str, Any]]:
        """Return a dictionary representing the monitoring schema with attributes."""
        return {
            "state": {"type": "TEXT"},
            "start_time": {"type": "TEXT"},
            "end_time": {"type": "TEXT"},
            "duration": {"type": "REAL"},
            "status": {"type": "TEXT"},
            "last_updated": {"type": "TEXT"},
            "num_requests": {"type": "INTEGER"},
            "successful_requests": {"type": "INTEGER"},
            "failed_requests": {"type": "INTEGER"},
            "requests_per_minute": {"type": "REAL"},
            "fault": {"type": "INTEGER"},
            "config": {"type": "DICT"}
        }
