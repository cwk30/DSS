from docplex.mp.model import Model


class BaseModel:
    """Basic data management code for all models"""
    
    SCHEMA = dict()
    
    def __init__(self, data):
        """Reads parameters according to schema."""
        
        # Basic parameters
        for table in self.SCHEMA:
            if table in data:
                self.__dict__[table] = data[table] # Defer exceptions till after patch
                
        # Check that data matches schema
        self._setup()
        self._validate_schema()
    
    def _compute_parameters(self):
        """processes data to meet schema requirements."""
        pass
        
    def _compute_indices(self):
        """Define sets of indices for later use."""
        pass
    
    def _validate_schema(self):
        """Ensures that processed data is of the same form as the schema"""
        for table in self.SCHEMA:
            if table not in self.__dict__:
                raise ValueError(f'`{table}` not found in data.')
            
            schema_cols = set(self.SCHEMA[table])
            table_cols = set(self.__dict__[table].reset_index().columns)
            missing_cols = schema_cols - table_cols
            if missing_cols:
                raise ValueError(f'`{missing_cols}` not found in `{table}`')
    
    def build(self, name=None, **kwargs):
        """Builds a docplex model."""
        # Initialize model
        model = Model(name=name, **kwargs)
        
        # Decision variables
        variables = self.variables(model)
        
        # Objective function
        objective = self.objective(variables)
        model.maximize(objective)
        
        # Constraints
        constraints = self.constraints(variables)
        for constraint_dict in constraints.values():
            model.add_constraints(constraint_dict.values())
        
        # Return completed model
        return model, variables, objective, constraints
    
    def variables(self, model):
        default_variables = dict()
        return default_variables
        
    def objective(self, variables):
        default_objective = 0
        return default_objective

    def constraints(self, variables):
        default_constraints = dict()
        return default_constraints
    
    
def mixin(schema,
          models=[],
          variables=[],
          objective=[],
          constraints=[],
          name=None):
    """Creates a base model that composes variable, objective and constraints from provided submodels.
    
    Priority (highest to lowest):
    1. Scoped models, from first to last.
    2. Common models, from first to last.
    """
    
    class ComposedModel(BaseModel):
        """Model that is composed from mixins"""
        
        SCHEMA = schema
        
        def _compute_parameters(self):
            base_models = constraints + objective + variables + models
            base_models = base_models[::-1]
            for base_model in base_models:
                base_model._compute_parameters(self)
                
        def _compute_indices(self):
            base_models = constraints + objective + variables + models
            base_models = base_models[::-1]
            for base_model in base_models:
                base_model._compute_indices(self)
        
        def variables(self, model):
            composed_variables = dict()
            base_models = models[::-1] + variables[::-1]
            for base_model in base_models:
                base_variables = base_model._variables(self, model)
                composed_variables.update(base_variables)
            return composed_variables
        
        def objective(self, variables):
            composed_objective = 0
            base_models = models[::-1] + objective[::-1] 
            for base_model in base_models:
                base_objective = base_model._objective(self, variables)
                composed_objective += base_objective
            return composed_objective
        
        def constraints(self, variables):
            composed_constraints = dict()
            base_models = models[::-1] + constraints[::-1]
            for base_model in base_models:
                base_constraints = base_model._constraints(self, variables)
                composed_constraints.update(base_constraints)
            return composed_constraints
        
    if name is not None:
        ComposedModel.__name__ = name
    
    return ComposedModel