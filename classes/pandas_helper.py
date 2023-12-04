from .field import Field
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

    def get_approval_process_ids( self ):
        """Gets a unique list of approval_process_ids and stores them as approval_process_ids. Will be passed into ReportGenerator instance to run get_proposals on."""

def concatenate_proposals (self, proposals): 
    """Concatenates the passed in proposals to form a single Pandas dataframe. Stores the dataframe as concatenated_dataframe."""

#proposals A list of JSON responses from running get_proposals on a ReportGenerator instance for approval_process_ids.

def filter_concatenated_proposals(self, filters):
    """Accepts a list of Filter instances and filters concatenated_dataframe in Pandas. Stores filtered dataframe as the new value on concatenated_dataframe."""

def sort_concatenated_proposals(self, sorting_rules): 
    """Accepts a list of SortingRule instances and sorts**concatenated_dataframe** in Pandas. Sorting is done by the first SortingRule followed by subsequent SortingRules, so SortingRule order matters. Stores sorted dataframe as the new value on concatenated_dataframe."""

def transform_column_names(self):
    """Loops over api_field_names checking for them in the concatenated_dataframe. If found, the column name is transformed to the user-friendly name stored in api_field_names."""

def get_relevant_columns(self, fields): 
    """
    Filters concatenated_dataframe to include only columns corresponding to the passed in fields. Stores the filtered dataframe as the new value on concatenated_dataframe.

    fields A list of Fields passed in from the ExcelInputParser instance that should appear in the output Excel Workbook."""

def get_additional_dataframes(self, field):
    """Using the passed in Field, concatenated_dataframe is filtered to create a new dataframe for each unique value found in the appropriate Field column. Additional dataframes are stored as entries in additional_dataframes. concatenated_dataframe is not mutated."""

def _get_unique_values(self, field): 
    """Using the passed in Field,identify unique values within a column of concatenated_dataframe. Stores unique values as additional_dataframe_names."""
