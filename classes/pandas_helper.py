from .field import Field
from .filter import Filter
from .sorting_rule import SortingRule
import pandas as pd
class PandasHelper:
    def __init__(self, proposal_list:list[Field], fields:list, sorting_rules, grouping_rule): 
        """proposal_list - The unfiltered list of proposals (in JSON) obtained via calling get_proposal_list on a ReportGenerator instance. The list is transformed to a Pandas dataframe at construction.

        fields - A list of Fields which should appear in the dataframes that will ultimately appear in the output Excel workbook.

        sorting_rules - A list of SortingRules which will be used to sort the pandas dataframes prior to writing the output Excel workbook.

        grouping_rule - A string indicating which field to use for creating additional_dataframes from concatenated_dataframes.
        """
        self.proposal_list = proposal_list
        self.fields = fields
        self.sorting_rules = sorting_rules
        self.grouping_rule = grouping_rule
        self.concatenated_dataframe = pd.DataFrame()
        self.additional_dataframes = []
        self.concatenate_proposals(self.proposal_list)


def concatenate_proposals (self, proposals): 
    """Concatenates the passed in proposals to form a single Pandas dataframe. Stores the dataframe as concatenated_dataframe."""
    concat_df = pd.DataFrame()
    for count, ele in enumerate(proposals, len(proposals)):
        concat_df = pd.concat([concat_df, pd.read_json(ele)])
    self.concatenated_dataframe = concat_df
    

def filter_concatenated_proposals(self, filters:Filter):
    """Accepts a list of Filter instances and filters concatenated_dataframe in Pandas. Stores filtered dataframe as the new value on concatenated_dataframe."""
    for filter_item in filters:
        if filter_item.operator == '>':
            self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] > filter_item.values[0]]
        elif filter_item.operator == '>=':
            self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] >= filter_item.values[0]]
        elif filter_item.operator == '<':
            self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] < filter_item.values[0]]
        elif filter_item.operator == '<=':
            self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] <= filter_item.values[0]]
        elif filter_item.operator == '=':
            self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] == filter_item.values[0]]
        elif filter_item.operator == '!=':
            self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] != filter_item.values[0]]
        elif filter_item.operator == 'IN':
            self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] in filter_item.values]
        elif filter_item.operator == 'NOT IN':
            self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name]  not in filter_item.values]
        elif filter_item.operator == 'BETWEEN':
            self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name].between(filter_item.values[0], filter_item.values[1])]

def sort_concatenated_proposals(self, sorting_rules:list[SortingRule]): 
    """Accepts a list of SortingRule instances and sorts**concatenated_dataframe** in Pandas. Sorting is done by the first SortingRule followed by subsequent SortingRules, so SortingRule order matters. Stores sorted dataframe as the new value on concatenated_dataframe."""
    self.convert_custom_sorts_to_categorical_columns(sorting_rules)
    columns = list(map(lambda sorting_rule: sorting_rule.field_name, sorting_rules))
    #Ascending works for custom bc pd.Categorical data type
    sort_orders = [sorting_rule.sort_order in ['Ascending', 'Custom'] for sorting_rule in sorting_rules]
    

def convert_custom_sorts_to_categorical_columns(self, sorting_rules: list[SortingRule]):
    """Accepts a list of sorting rules. For sorting rules with a 'Custom' sort, their corresponding pandas column is converted to a Categorical type to allow for custom sorting."""
    for sorting_rule in sorting_rules:
        if sorting_rule.sort_order == 'Custom':
            self.concatenate_dataframe[sorting_rule.field_name] = pd.Categorical(self.concatenate_dataframe[sorting_rule.field], sorting_rule.values)

def transform_column_names(self):
    """Loops over api_field_names checking for them in the concatenated_dataframe. If found, the column name is transformed to the user-friendly name stored in api_field_names."""

def get_relevant_columns(self, fields): 
    """
    Filters concatenated_dataframe to include only columns corresponding to the passed in fields. Stores the filtered dataframe as the new value on concatenated_dataframe.

    fields A list of Fields passed in from the ExcelInputParser instance that should appear in the output Excel Workbook."""
    columns = list(map(lambda field: field.field_name, fields))
    self.concatenated_dataframe = self.concatenated_dataframe[columns]

def get_additional_dataframes(self, field):
    """Using the passed in Field, concatenated_dataframe is filtered to create a new dataframe for each unique value found in the appropriate Field column. Additional dataframes are stored as entries in additional_dataframes. concatenated_dataframe is not mutated."""
    self.get_additional_dataframe_names(field)
    for additional_dataframe_name in self.additional_dataframe_names:
        additional_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[field.field_name] == additional_dataframe_name]
        self.additional_dataframes.append(additional_dataframe)
    

def get_additional_dataframe_names(self, field:Field): 
    """Using the passed in Field,identify unique values within a column of concatenated_dataframe. Stores unique values as additional_dataframe_names."""
    self.additional_dataframe_names = list(self.concatenated_dataframe[field.field_name].unique())
