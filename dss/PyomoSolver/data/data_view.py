from .excel_io import ExcelIO
from .database_io import DatabaseIO

class DataView(DatabaseIO,
               ExcelIO):
    """Wrapper to bind all IO methods to the base class."""
    pass
