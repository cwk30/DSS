from .base_view import BaseView

class DatabaseIO(BaseView):
    @classmethod
    def add_table_from_query(cls, sql, con, domain=[]):
        pass