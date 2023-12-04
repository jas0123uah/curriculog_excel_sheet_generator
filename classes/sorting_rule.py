class SortingRule:
    import typing
    def init(self, field_name, sort_by:typing.Literal['Ascending', 'Descending', 'Custom'], values:list[str]): 
        """Constructor for SortingRule instance.

        field_name is the name of the column in the pandas dataframe that should be used for sorting.

        sort_by indicates the type of sorting that should occur in the dataframe based on the column/field_name. Valid sort_bys include 'Ascending', 'Descending', and 'Custom'.

        values is a list of values to sort by for a given column/field_name. Values that appear first in the list are sorted before values that appear later in the list. This parameter defaults to None and is only relevant if sort_by is "Custom".
        """
        self.field_name = field_name
        self.sort_by = sort_by
        self.values = values
