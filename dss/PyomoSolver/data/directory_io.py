import json
import os
from pathlib import Path
import pandas as pd
from .base_view import BaseView

class DirectoryIO(BaseView):
    """Read from and write to friendlier directory format"""
    
    @classmethod
    def from_directory(cls, root, domain):
        """Reads data from a excel files in a nested directory structure."""
        
        # Read metadata
        with Path(root, 'metadata.json').open('r') as file:
            meta = json.load(file)
        ignore = meta['ignore']
        level_names = meta['data_levels']
        depth = len(level_names)
        
        # Collect all filepaths in the tree
        tree = list()
        nodes = [Path(root)]
        while nodes:
            node = nodes.pop()
            if node.is_file():
                tree.append(node)
            elif node.is_dir():
                nodes.extend(list(node.iterdir()))
        
        # Filter and extract info from the tree
        tree = [path for path in tree if path.stem not in [*ignore, 'metadata']]
        levels = [[*path.parts[-depth:][:-1], path.stem] for path in tree]    
        tables = [pd.read_excel(path, sheet_name=None) for path in tree]
        
        # Reshape data for concatenation
        for level, table in zip(levels, tables):
            for table_name in table:
                if table_name in level_names:
                    table[table_name] = table[table_name].set_index('variable').T
                else:
                    table[table_name][level_names[-1]] = level[-1]
        
        # Group data for concatenation
        attrs = dict()
        for table in tables:
            for name in table:
                attrs[name] = attrs.get(name, list())
                attrs[name].append(table[name])
                
        # Concatenate data into original tables
        for name in attrs:
            df = pd.concat(attrs[name])
            df = df.reset_index(drop=True)
            attrs[name] = df
        
        # Add ignored tables
        for name in ignore:
            file = Path(root, name + '.xlsx')
            attrs[name] = pd.read_excel(file)
            
        # Format domain tables with id cols
        for domain_name in domain:
            if 'id' not in attrs[domain_name]:
                attrs[domain_name].index.name = 'id'
        
        # Replace domain columns with indices
        for domain_name in domain[::-1]:
            lookup = attrs[domain_name]
            lookup = lookup.reset_index().set_index(domain_name)    
            for attr_name, attr in attrs.items():
                if attr_name not in domain and domain_name in attr:
                    attr[domain_name] = lookup['id'][attr[domain_name]].values
        
        return cls(tables=attrs, domain=domain)
            
    def to_directory(self, root, data_table, data_levels, ignore=None):
        """Writes the tree format to excel files in a nested directory structure."""
        # Write root
        Path(root).mkdir(parents=True, exist_ok=True)
        
        meta = {
            'data_table': data_table,
            'data_levels': data_levels,
        }
        
        if ignore is not None:
            meta.update({'ignore': ignore})
            for table in ignore:
                file = Path(root, table + '.xlsx')
                self[table].reset_index(drop=True).to_excel(file)
         
        with Path(root, 'metadata.json').open('w') as file:
            json.dump(meta, file)
        
        # Write branches
        branches = self._branches(data_table, data_levels, ignore=ignore)
        for branch, leaf in branches.items():
            if isinstance(branch, str):
                file = Path(root, branch + '.xlsx')
            else:
                *parts, filename = branch
                file = Path(root, *parts, filename + '.xlsx')
            
            file.parent.mkdir(parents=True, exist_ok=True)
            with pd.ExcelWriter(file) as writer:
                for item in leaf:
                    leaf[item].to_excel(writer, sheet_name=item, index=False)
    
    def tree(self, data_table, data_levels, ignore=None):
        """Returns the data in a tree format using a specified table's fields as branches 
        from the root."""
        branches = self._branches(data_table, data_levels, ignore=ignore)
        
        if all(isinstance(branch, str) for branch in branches):
            tree = branches
            
        else:
            tree = dict()
            for branch, leaf in branches.items():
                layer = tree
                for node in branch:
                    layer[node] = layer.get(node, dict())
                    layer = layer[node]
                for item in leaf:
                    layer[item] = leaf[item]
        
        return tree
    
    def _branches(self, data_table, data_levels, ignore=None):
        """Uses the specified table's fields to create branches of a tree."""
        first = self.tables[data_table].groupby(data_levels)
        paths = first.agg(lambda x: None).index
        attrs = first.apply(pd.melt)
        branches = dict()
        
        if ignore is None:
            tables = self.tables
        else:
            tables = [table for table in self.tables if table not in ignore]
        
        for path in paths:
            branches[path] = branches.get(path, dict())
            for table in tables:
                if table == data_table and path in attrs.index:
                    df = attrs.loc[path]
                elif table != data_table and data_table in self[table]:
                    df = self[table]
                    name = path if isinstance(path, str) else path[-1]
                    mask = df[data_table] == name
                    df = df[mask]   
                    df = df.drop(columns=data_table)
                    df = df.reset_index(drop=True)
                else:
                    continue
                
                # Add branch if there is a leaf
                if not df.empty:
                    branches[path][table] = df
        
        return dict(branches.items())
