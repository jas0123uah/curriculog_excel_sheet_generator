
class Filter:
    import typing
    def __init__(self, field_name:str, operator: typing.Literal['>', '>=', '<', '<=', '=', '!=', 'IN', 'NOT IN', 'BETWEEN'], values:list[str]): 
        """Constructor for Filter instance.

        field_name is the name of the column in the pandas dataframe that should be used for filtering.

        operator indicates how the column should be filtered in the pandas dataframe. Valid operators include mathematical operators (>, >=, <, <=, =, !=), IN, NOT IN, and BETWEEN.

        values is a list of values to utilize for filtering. If the operator is a mathematical operator, there should only ever be one value in the list. If the operator is BETWEEN, there should only be two values in the list, corresponding to the lower (inclusive) and upper (exclusive) range of acceptable values. If the operator is IN or NOT IN any number of values may be in the values list."""
        if operator not in ['>', '>=', '<', '<=', '=', '!=', 'IN', 'NOT IN', 'BETWEEN']:
            raise ValueError(f"Invalid operator: {operator} operator must be >, >=, <, <=, =, !=, IN, NOT IN, or BETWEEN")
        self.field_name = field_name
        self.operator = operator
        self.values = [value.strip() for value in values]
