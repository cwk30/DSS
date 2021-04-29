import pandas as pd


class BaseView:
    """A dict of tables with a specified domain. All indices will be automatically
    replaced with human readable text using the domain tables as a lookup.
    
    Arguments
    ---------
    tables: dict[str, pd.DataFrame]
    A dict of tables.
    
    domain: List[str]
    A list of keys for the domain tables to be used for linking.
    """
    
    def __init__(self, tables, domain=[]):
        """Initializes a set of tables, optionally specifying a domain for indices."""
        self.domain = domain
        self.tables = tables
        self.aliases = dict()
        
        self._ensure_dtypes()
        self._build_aliases()
        self._ensure_aliasing()
            
    def _ensure_dtypes(self):
        """Ensure tables are of the correct data type"""
        for k, v in self.tables.items():
            self.tables[k] = v.apply(pd.to_numeric, errors='ignore')
        
    def _build_aliases(self):
        """Builds alias tables from table and domain"""
        for domain_name in self.domain:
            try:
                # Check and format the domain sheets for linking
                table = self.tables[domain_name]
                table.index.name = 'id'
            except:
                raise IndexError(f'Domain "{domain_name}" is not in tables')
            try:
                # Build alias tables for linking
                value = table[domain_name].values
                alias = table.index
                self.aliases[domain_name] = pd.DataFrame(alias, index=value)
            except:
                raise IndexError(f'"{domain_name}" must be a column in table "{domain_name}"')
    
    def _ensure_aliasing(self):  
        """Ensure domain columns are aliased in tables"""
        for k, v in self.tables.items():
            if k not in self.domain:
                self.tables[k] = self.alias(v)        

    def alias(self, table):            
        """Replaces names from domain with unique indices"""
        levels = list()
        table = table.copy()
        
        for domain_name in self.domain:
            alias = self.aliases[domain_name]
            
            for column_name in table.columns:
                if domain_name in str(column_name):
                    levels.append(column_name)
                    value = table[column_name]
                    table[column_name] = alias.loc[value].values
            
#             if domain_name in table.columns:
#                 levels.append(domain_name)
#                 value = table[domain_name]
#                 table[domain_name] = alias.loc[value].values
        
        if levels:
            table = table.set_index(levels)
            
        return table
    
    def antialias(self, table):
        """Try to apply names from the domain to a table"""
        if self.domain is not None:
            for domain_name in self.domain[::-1]:
                for index_name in table.index.names[::-1]:
                    if domain_name in index_name:
                        label = self.tables[domain_name][domain_name]
                        table = pd.merge(label, table, left_index=True, right_on=index_name)
                        table = table.rename(columns={domain_name: index_name})
                
        return table
     
    
    def copy(self):
        """Returns a deep copy"""
        return type(self)({k:v.copy() for k,v in self.tables.items()}, self.domain)
        
    def view(self, key):
        """Returns a table with indices replaced by names from the domain"""
        return self.antialias(self.tables[key])

    
    def __iter__(self):
        """Wrapper of iterator protocol for `self.tables`"""
        return self.tables.__iter__()
    
    def __next___(self):
        """Wrapper of iterator protocol for `self.tables`"""
        return self.tables.__next__()
        
    def __getitem__(self, key):
        """Emulate dict behaviour"""
        return self.tables[key]
        
    def __setitem__(self, key, val):
        """Emulate dict behaviour"""
        self.tables[key] = val
        
    def __repr__(self):
        """Nicely formatted print form"""
        def linebreak(symbol): return '\n' + 80*symbol + '\n'
        return '\n'.join(linebreak('=') + name + linebreak('-') + repr(table)
                         for name, table in self.tables.items())
