class Field:
    from .filter import Filter
    def __init__(self, field_name:str,  comment_field:str, filters:list[Filter]):
        """Constructor for Field instance.

        field_name is the user-friendly name of the column field should have in the output Excel workbook.
        comment_field indicates what comment text cells in the column for the field_name should have.

        filters List of Filters which should be applied to the field when filtering the Pandas dataframe via the PandasHelper class instance."""
        self.field_name = field_name
        self.comment_field = comment_field
        self.filters = filters
    
