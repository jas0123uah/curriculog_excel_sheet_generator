class ExcelInputParser:
    def init(self, input_workbook): 
        """Constructor for ExcelInputParser instance. Accepts the path to an Excel Workbook"""
        self.workbook = ''

    def parse_workbook(self): 
        """Primary function to parse input Excel workbook. Makes use of helper functions _get_requested_fields, _get_field_filters, _get_field_comment to parse input excel workbook"""

    def _get_requested_fields(self): 
        """Parses the Field column in the Excel workbook to identify which proposal fields are needed from the Curriculog API. Returns an array/list of Field instances which contain filtering information specific to the Field for passing to the PandasHelper constructor ."""

    def _get_field_filters(self, row): 
        """For a given row in the Field column in the Excel workbook, identify the Filter for that field."""

    def _get_field_comment(self, row): 
        """For a given row in the Field column in the Excel workbook, identify the proposal_field which should be used as a comment."""

    def _get_approval_processes_ids(self, row): 
        """Parses the Approval Proccesses Columns to return a list of approval processes that should be kept in the proposal_list. This method uses a lookup to match an approval process name to its ap_id found in the curriculog API. This list should be passed the ReportGenerator get_proposal_fields method"""

    def get_sorting_rules(self): 
        """Parses the Sort By, Sort Order, and Custom Sort columns to create an array of SortingRules. Returns a list of SortingRules to pass to the PandasHelper constructor."""

    def get_grouping_rule(self): 
        """Parses the Separate sheets by column to get the field which should be used for creating additional_dataframes in the PandasHelper instance. Return value is passed to the PandasHelper constructor."""
