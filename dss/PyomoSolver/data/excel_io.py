import pandas as pd
from .base_view import BaseView

class ExcelIO(BaseView):
    """Reads an excel workbook and converts each sheet into a table. Sheet names
    containing the tables that form the domain for the indices should be passed to
    enable automatic linking of indices to human readable names.
    
    Arguments
    ---------
    io : file, str
    A file object or filepath to pass to `pd.read_excel`.
    
    domain: List[str] = None
    A list of sheet names to use as indices for all tables, if they are found in the
    columns. Sheets supplied to `domain` must have an 'id' field and a 'name' field.
    
    """
    
    @classmethod
    def from_excel(cls, io, domain=None):
        """Initializes a table for each sheet in an excel workbook."""
        sheets = pd.read_excel(io, sheet_name=None)
        
#         aliases = dict()
#         for domain_name in domain:
            
#             # Check and format the domain sheets for linking
#             try:
#                 table = sheets[domain_name]
#                 table.index.name = 'id'
#             except:
#                 raise IndexError(f'Domain "{domain_name}" is not a sheet')
            
#             # Build alias tables for linking
#             try:
#                 value = table[domain_name].values
#                 alias = table.index
#                 aliases[domain_name] = pd.DataFrame(alias, index=value)
#             except:
#                 raise IndexError(f'"{domain_name}" must be a column in sheet "{domain_name}"')
                
#         for sheet_name in sheets:
#             if sheet_name not in domain:
#                 sheet = sheets[sheet_name]
#                 levels = list()

#                 for domain_name in domain:
#                     alias = aliases[domain_name]
#                     if domain_name in sheet:
#                         levels.append(domain_name)
#                         value = sheet[domain_name]
#                         sheet[domain_name] = alias.loc[value].values

#                 if levels:
#                     sheets[sheet_name] = sheet.set_index(levels)
                
        return cls(tables=sheets, domain=domain)

    def to_excel(self, io):
        """Writes each table to a coresponding sheet using the supplied io"""
        with pd.ExcelWriter(io) as writer:
            for name in self.tables:
                self.view(name).to_excel(writer, sheet_name=name, index=True)
