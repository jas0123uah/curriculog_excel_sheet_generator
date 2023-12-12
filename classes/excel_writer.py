from openpyxl.comments import Comment
from openpyxl.utils.dataframe import dataframe_to_rows
class ExcelWriter:
    import pandas as pd
    from .field import Field
    #from openpyxl.comments import Comment
    def __init__(self, concatenated_dataframe:pd.DataFrame, additional_dataframes:list[pd.DataFrame] ): 
        """Constructor for ExcelWriter instance. Converts dataframes to rows with openpyxl's dataframe_to_rows. concatenated_dataframe is stored as concatenated_rows. additional_dataframes are stored as additional_rows"""
        self.col_lookup = {}

    def create_workbook(self): 
        """Creates an output Excel workbook titled 'output_TIMESTAMP'.xlsx TIMESTAMP is the current timestamp when the output Excel workbook is being generated. The first sheet titled "Main" is the concatenated_rows. Additional sheets correspond to additional_rows , with the sheets having names corresponding to additional_dataframe_names."""

    def _convert_dataframe_to_workbook_worksheet(self, dataframe):
        """Given a pandas dataframe add it to an existing workbook as a single worksheet.."""
        #https://stackoverflow.com/questions/36657288/copy-pandas-dataframe-to-excel-using-openpyxl
        
    def get_column_names_needing_comments(self, fields:list[Field]): 
        """Loops over a list of fields to determine which should have a comment. Excel columns which should have comments are stored as column_names_needing_comments."""
        ### Map over fields, returning field_name
        column_names = ''
        self.column_names_needing_comments = column_names

    def find_cells_needing_comment(self, row): 
        """Given an input row use column_names_needing_comments to find which cells in a row need a comment."""
        ##Get column in row needing comment.
        cell_needing_comment = ''
        ##Find other column which contains the comment text
        cell_with_comment = self.find_cell_containing_comment(row, column_name)
        ##Call set_cell_comment
        self.set_cell_comment(cell_needing_comment, )

    def find_cell_containing_comment(self, row:pd.Series, column_name:str): 
        """Given an input row and column_name, find the cell containing the comment as its value and return that value."""
        

    def set_cell_comment(self, cell, comment_text:str): 
        """Set a given cell's comment."""
        comment = Comment(comment_text, 'OpenPyxl')
        cell.comment = comment
    def get_column_indices_by_name(self):
        """Create a lookup of column names and indices for the given column name. Lookup used for manipulating data in spreadsheet."""
        col_lookup = {}
        column_idx  = 0
        for col in self.current_sheet.iter_cols(1, self.current_sheet.max_column):
            col_lookup[col[0].value] = column_idx
            column_idx += 1
        self.col_lookup = col_lookup
    def delete_comment_columns(self): 
        """Delete columns from rows which contain comment text as a value. (Comments are stored as fields in the pandas dataframe this step removes those columns)."""
        #Loop over column_names_needing_comments
        
        col_idx = self.col_lookup[col_name]
        self.current_sheet.delete_cols(col_idx, 1)
