class ExcelWriter:
    import pandas as pd
    from .field import Field
    def __init__(self, concatenated_dataframe:pd.DataFrame, additional_dataframes:list[pd.DataFrame] ): 
        """Constructor for ExcelWriter instance. Converts dataframes to rows with openpyxl's dataframe_to_rows. concatenated_dataframe is stored as concatenated_rows. additional_dataframes are stored as additional_rows"""

    def create_workbook(self): 
        """Creates an output Excel workbook titled 'output_TIMESTAMP'.xlsx TIMESTAMP is the current timestamp when the output Excel workbook is being generated. The first sheet titled "Main" is the concatenated_rows. Additional sheets correspond to additional_rows , with the sheets having names corresponding to additional_dataframe_names."""

    def get_columns_needing_comments(self, fields:list[Field]): 
        """Loops over a list of fields to determine which should have a comment. Excel columns which should have comments are stored as column_names_needing_comments."""

    def find_cells_needing_comment(self, row:pd.Series): 
        """Given an input row use column_names_needing_comments to find which cells in a row need a comment."""

    def find_cells_containing_comment(self, row:pd.Series, column_name:str): 
        """Given an input row and column_name, find the cell containing the comment as its value and return that value."""

    def set_cell_comment(self, cell, comment_text:str): 
        """Set a given cell's comment."""

    def delete_comment_columns(self, rows): 
        """Delete columns from rows which contain comment text as a value. (Comments are stored as fields in the pandas dataframe this step removes those columns)"""
