from core.utils import Utils
from datetime import datetime
from jsonpath_ng import parse

class BaseFormatter:
    def __init__(self):
        self.logger = Utils.get_logger()

    def clean_text(self, text):
        """Clean and normalize text data."""
        if not text:
            return ""
        return text.strip().lower()

    def convert_to_int(self, value):
        """Convert a value to integer."""
        if isinstance(value, str) and value.isdigit():
            return int(value)
        try:
            return int(value)
        except (ValueError, TypeError):
            self.logger.warning(f"Failed to convert {value} to int")
            return None

    def convert_to_float(self, value):
        """Convert a value to float."""
        try:
            cleaned_value = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
            return float(cleaned_value)
        except (ValueError, TypeError):
            self.logger.warning(f"Failed to convert {value} to float")
            return None

    def parse_date(self, date_input, date_format="%Y-%m-%d", timestamp_unit="ms"):
        """Parse a date string or timestamp into a date object."""
        try:
            if isinstance(date_input, int):
                # Convert timestamp based on the provided unit (default is milliseconds)
                if timestamp_unit == "ms":
                    return datetime.fromtimestamp(date_input / 1000.0)
                elif timestamp_unit == "s":
                    return datetime.fromtimestamp(date_input)
                else:
                    self.logger.warning(f"Unsupported timestamp unit: {timestamp_unit}")
                    return None
            elif isinstance(date_input, str):
                if not date_input:
                    # Return the current date if date_input is an empty string
                    return datetime.now()
                return datetime.strptime(date_input, date_format)
            else:
                self.logger.warning(f"Unsupported date input type: {type(date_input)}") if date_input else None
                return datetime.now()
        except ValueError:
            self.logger.warning(f"Failed to parse date {date_input} with format {date_format} ,  using current date.")
            return datetime.now()
        
    def format_data(self, raw_data):
        """Format raw data according to specific rules (to be implemented by subclasses)."""
        raise NotImplementedError("Subclasses should implement this method")
    
    def get_json_value(self,data, json_paths, return_all=False):
        """
        Retrieve values from JSON data based on JSON paths.

        :param data: The JSON data (dict) from which to extract values.
        :param json_paths: A string or list of strings representing JSON paths.
        :param return_all: Boolean indicating whether to return all matches as a list. Defaults to False.
        :return: The first non-null value or a list of all values if return_all is True.
        """
        if isinstance(json_paths, str):
            json_paths = [json_paths]

        results = []
        for path in json_paths:
            jsonpath_expr = parse(path)
            matches = [match.value for match in jsonpath_expr.find(data)]
            results.extend(matches)
            if not return_all:
                for match in matches:
                    if match is not None:
                        return match

        return results if return_all else (results[0] if results else None)
