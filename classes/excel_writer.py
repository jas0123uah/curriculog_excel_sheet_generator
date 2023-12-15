from openpyxl.comments import Comment
from openpyxl.utils.dataframe import dataframe_to_rows
import openpyxl

from pprint import pprint
class ExcelWriter:
    import pandas as pd
    from .field import Field
    #from openpyxl.comments import Comment
    def __init__(self, concatenated_dataframe:pd.DataFrame, additional_dataframes:list[pd.DataFrame], fields:list[Field] ): 
        """Constructor for ExcelWriter instance. Converts dataframes to rows with openpyxl's dataframe_to_rows. concatenated_dataframe is stored as concatenated_rows. additional_dataframes are stored as additional_rows"""
        self.col_lookup = {}
        self.target_comment_column_map = {}
        self.concatenated_dataframe = concatenated_dataframe
        self.additional_dataframes = additional_dataframes
        self.fields = fields
        self.workbook = openpyxl.load_workbook('./test.xlsx')
        self.current_sheet = self.workbook.active
        for field in self.fields:
            if field.comment_field:
                self.target_comment_column_map[field.field_name] = field.comment_field
        
        self.get_column_indices_by_name()

    def create_workbook(self): 
        """Creates an output Excel workbook titled 'output_TIMESTAMP'.xlsx TIMESTAMP is the current timestamp when the output Excel workbook is being generated. The first sheet titled "Main" is the concatenated_rows. Additional sheets correspond to additional_rows , with the sheets having names corresponding to additional_dataframe_names."""
        
        ##Convert dataframe
        #self._convert_dataframe_to_workbook_worksheet(self.concatenated_dataframe)
        self.get_column_names_needing_comments()
        for row in self.workbook.active.iter_rows():
            
            self.set_cells_needing_comment(row)
        self.delete_comment_columns()
        self.workbook.save('my_workbook.xlsx')
        
        
    def get_column_names_needing_comments(self): 
        """Loops over a list of fields to determine which should have a comment. Excel columns which should have comments are stored as column_names_needing_comments."""
        ### Map over fields, returning field_name
        column_names = []
        for field in self.fields:
            if field.comment_field:
                column_names.append(field.comment_field)
        self.column_names_needing_comments = column_names

    def set_cells_needing_comment(self, row): 
        """Given an input row use column_names_needing_comments to find which cells in a row need a comment and give them a comment."""
        ##Loop over a dict mapping columns that need comments (target columns) to (comment_columns)
        print(self.target_comment_column_map)
        for target_column, comment_column in self.target_comment_column_map.items():
            
            ##Get cell in row needing comment.
            cell_needing_comment = self.find_cell_by_column(row, target_column )
            ##Find other column which contains the comment text
            cell_with_comment = self.find_cell_by_column(row, comment_column)
            ##Call set_cell_comment IGNORES THE HEADER
            if cell_with_comment.value != comment_column:
                self.set_cell_comment(cell_needing_comment, cell_with_comment.value)

    def find_cell_by_column(self, row:pd.Series, column_name:str): 
        """Given an input row and column_name, find the cell corresponding to column_name and return its value."""
        print(f'COLUMN LOOKUP:{self.col_lookup}')
        
        idx = self.col_lookup[column_name]
        
        target_cell = list(filter(lambda cell: cell.column == idx +1, row))[0]
        return target_cell

    def set_cell_comment(self, cell, comment_text:str): 
        """Set a given cell's comment."""
        comment = Comment(comment_text, 'OpenPyxl')
        cell.comment = comment
    def get_column_indices_by_name(self):
        """Create a lookup of column names and indices for the given column name. Lookup used for manipulating data in spreadsheet."""
        #https://stackoverflow.com/questions/51478413/select-a-column-by-its-name-openpyxl
        col_lookup = {}
        column_idx  = 0
        for col in self.current_sheet.iter_cols(1, self.current_sheet.max_column):
            col_lookup[col[0].value] = column_idx
            column_idx += 1
        self.col_lookup = col_lookup
    def delete_comment_columns(self): 
        """Delete columns from rows which contain comment text as a value. (Comments are stored as fields in the pandas dataframe this step removes those columns)."""
        #Loop over column_names_needing_comments
        for col_name in self.column_names_needing_comments:
            col_idx = self.col_lookup[col_name]
            self.workbook.active.delete_cols(col_idx+1, 1)
