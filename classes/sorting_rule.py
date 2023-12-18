class SortingRule:
    import typing
    def __init__(self, field_name, sort_order:typing.Literal['Ascending', 'Descending', 'Custom'], values:list[str]): 
        """Constructor for SortingRule instance.

        field_name is the name of the column in the pandas dataframe that should be used for sorting.

        sort_order indicates the type of sorting that should occur in the dataframe based on the column/field_name. Valid sort_orders include 'Ascending', 'Descending', and 'Custom'.

        values is a list of values to sort by for a given column/field_name. Values that appear first in the list are sorted before values that appear later in the list. This parameter defaults to None and is only relevant if sort_order is "Custom".
        """
        self.field_name = field_name
        self.sort_order = sort_order
        self.values = values
