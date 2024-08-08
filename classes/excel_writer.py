import openpyxl, re, os
from openpyxl.comments import Comment
from openpyxl.styles import Color, PatternFill, Font
from openpyxl.workbook.child import INVALID_TITLE_REGEX
from datetime import datetime
class ExcelWriter:
    import pandas as pd
    from .field import Field
    def __init__(self, concatenated_dataframe:pd.DataFrame, additional_dataframes:list[pd.DataFrame], fields:list[Field], grouping_rule:str, report_name:str ): 
        """Constructor for ExcelWriter instance. Converts dataframes to rows with openpyxl's dataframe_to_rows. concatenated_dataframe is stored as concatenated_rows. additional_dataframes are stored as additional_rows"""
        self.col_lookup = {}
        self.target_comment_column_map = {}
        self.columns_with_embedded_urls = []
        self.concatenated_dataframe = concatenated_dataframe
        self.additional_dataframes = additional_dataframes
        self.additional_workbook_paths = {}
        self.report_name = report_name
        #Write the additional dataframes we have to Excel workbooks. OpenPyxl doesn't play nice w/ pandas dfs, but does load xlsx files fine.
        for df_data in self.additional_dataframes:
            for df_name, df in df_data.items():
                df_name = re.sub(INVALID_TITLE_REGEX, '_', df_name)
                #Excel sheet titles can't be > 31 characters. Trimming to supress warning message.
                if len(df_name) > 31:
                    df_name = df_name[:31]
                #Happens in cases where one of the values in the group by is empty
                if df_name == '':
                    df_name = 'EMPTY'
                df.to_excel(f'additional_dataframe_{df_name}.xlsx', sheet_name=df_name)
                self.additional_workbook_paths[df_name] = f'additional_dataframe_{df_name}.xlsx'
        self.additional_workbooks = [{sheet_name: openpyxl.load_workbook(additional_workbook_path)} for sheet_name, additional_workbook_path in self.additional_workbook_paths.items()]
        self.fields = fields
        self.grouping_rule = grouping_rule
        self.workbook = openpyxl.load_workbook('./test.xlsx')
        self.workbook.active.title = 'Main'
        self.current_sheet = self.workbook.active
        for field in self.fields:
            if field.comment_field:
                self.target_comment_column_map[field.field_name] = field.comment_field
            if field.embed_url:
                self.columns_with_embedded_urls.append(field.field_name)
        
        self.get_column_indices_by_name()

    def create_workbook(self): 
        """Creates an output Excel workbook titled 'output_TIMESTAMP'.xlsx TIMESTAMP is the current timestamp when the output Excel workbook is being generated. The first sheet titled "Main" is the concatenated_rows. Additional sheets correspond to additional_rows , with the sheets having names corresponding to additional_dataframe_names."""
        
        self.get_column_names_needing_comments()
        for row in self.workbook.active.iter_rows():
            self.set_cells_needing_comment(row)
            self.set_cells_needing_embedded_url(row)
            self.format_impact_cell(row)
        self.delete_comment_columns(self.workbook.active)
        self.delete_group_by_col_name(self.workbook.active)
        self.add_additional_sheets()
        #Current timestamp in YYYY-MM-DD-HH-MM-SS format using 12 hour clock
        now = datetime.now().strftime('%Y_%m_%d_%I_%M_%p')
        output_dir = f'./output/{self.report_name}/current_report/'
        prev_output_dir = f'./output/{self.report_name}/previous_report/'
        os.makedirs(prev_output_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        # Move files in output directory to previous output directory
        for file in os.listdir(output_dir):
            os.rename(f'{output_dir}{file}', f'{prev_output_dir}{file}')
        
        #Write output workbook
        self.workbook.save(f'{output_dir}{now}.xlsx')
        self.delete_temp_workbooks()
        
    def add_additional_sheets(self):
        """Adds sheets for workbooks in self.additional_workbooks."""
        for wb_container in self.additional_workbooks:
            for sheet_name, additional_workbook in wb_container.items():
                additional_sheet = self.workbook.create_sheet(sheet_name)
                for i in range(1, additional_workbook.active.max_row+1): 
                    
                    for j in range(1, additional_workbook.active.max_column+1): 
                        cell_obj = additional_workbook.active.cell(row=i, column=j) 
                        additional_sheet.cell(row=i, column=j).value = cell_obj.value
                        if(i == 1 or j == 1):
                            additional_sheet.cell(row=i, column=j).style = 'Pandas'
            
                for row in additional_sheet.iter_rows():
                    self.format_impact_cell(row)
                    self.set_cells_needing_comment(row)
                    self.set_cells_needing_embedded_url(row)
                self.delete_comment_columns(additional_sheet)
                self.delete_group_by_col_name(additional_sheet)
    
    def delete_temp_workbooks(self):
        """Delete the workbooks we temporarily created due to openpyxl not playing nice with pandas."""
        #os.remove('test.xlsx')
        for temp_workbook in self.additional_workbook_paths.values():
            os.remove(temp_workbook)
        
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
        for target_column, comment_column in self.target_comment_column_map.items():
            
            ##Get cell in row needing comment.
            cell_needing_comment = self.find_cell_by_column(row, target_column )
            ##Find other column which contains the comment text
            cell_with_comment = self.find_cell_by_column(row, comment_column)
            ##Call set_cell_comment IF CHECK IGNORES THE HEADER
            if cell_with_comment.value != comment_column:
                self.set_cell_comment(cell_needing_comment, cell_with_comment.value)
    def set_cells_needing_embedded_url(self, row):
        """Given an input row use columns_with_embedded_urls to find which cells in a row need the proposal url embedded and embed the url.""" 
        for column_name in self.columns_with_embedded_urls:
            cell_needing_embedded_url = self.find_cell_by_column(row, column_name)
            cell_with_embedded_url = self.find_cell_by_column(row, 'URL')
            url = cell_with_embedded_url.value
            if cell_needing_embedded_url.value!= column_name:
                cell_needing_embedded_url.hyperlink = url
                cell_needing_embedded_url.style = 'Hyperlink'
    def find_cell_by_column(self, row, column_name:str): 
        """Given an input row and column_name, find the cell corresponding to column_name and return its value."""
        
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
    def delete_comment_columns(self, worksheet): 
        """Delete columns from rows which contain comment text as a value. (Comments are stored as fields in the pandas dataframe this step removes those columns)."""
        #Loop over column_names_needing_comments
        for col_name in self.column_names_needing_comments:
            col_idx = self.col_lookup[col_name]
            worksheet.delete_cols(col_idx+1, 1)
    def delete_group_by_col_name(self,worksheet):
        """Looks for a column used to create additional sheets in the output excel workbook. If that field was not requested, that column is deleted."""
        requested_columns = list(map(lambda field: field.field_name, self.fields))
        if self.grouping_rule and self.grouping_rule not in requested_columns:
            col_idx = self.col_lookup[self.grouping_rule]
            worksheet.delete_cols(col_idx, 1) 
    
    def get_impact_color(self, impact):
        """Returns the color the cell should be based on its impact"""
        red_fill = PatternFill(start_color='FFC7CE',
                   end_color='FFC7CE',
                   fill_type='solid')
        gold_fill = PatternFill(start_color='FFEB9C',
                   end_color='FFEB9C',
                   fill_type='solid')
        green_fill = PatternFill(start_color='C6EFCC',
                   end_color='C6EFCC',
                   fill_type='solid')
        
        if impact == 'High':
            return red_fill
        elif impact == 'Mid':
            return gold_fill
            
        elif impact == 'Low':
            return green_fill
        else:
            return None
    
    def get_text_color(self, impact):
        if impact == 'High':
            return Color(rgb='9C0006')
        elif impact == 'Mid':
            return Color(rgb='9C5700')
        elif impact == 'Low':
            return Color(rgb='006100')
    def format_impact_cell(self, row):
        """Function for formatting the impact column cells with proper background and font color"""
        cell = self.find_cell_by_column(row, 'Impact Level')
        cell_color = self.get_impact_color(cell.value)
        text_color = self.get_text_color(cell.value)
        if cell_color != None:
            cell.fill = cell_color #https://stackoverflow.com/questions/30484220/fill-cells-with-colors-using-openpyxl
            cell.font = Font(color=text_color)
