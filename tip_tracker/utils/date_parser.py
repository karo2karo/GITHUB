"""Date parsing utilities."""

from datetime import datetime


class DateParser:
    @staticmethod
    def parse_date_string(date_string, format_string="%Y-%m-%d"):
        """Parse date string into datetime object."""
        if not date_string:
            return None
        try:
            return datetime.strptime(date_string, format_string)
        except ValueError:
            return None
    
    @staticmethod
    def format_datetime(dt, format_string="%Y-%m-%d %H:%M"):
        """Format datetime object to string."""
        if isinstance(dt, datetime):
            return dt.strftime(format_string)
        return str(dt)
    
    @staticmethod
    def format_date(dt, format_string="%Y-%m-%d"):
        """Format datetime object to date string."""
        if isinstance(dt, datetime):
            return dt.strftime(format_string)
        return str(dt)