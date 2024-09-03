import tkinter as tk
from tkinter import messagebox
import os
from decouple import config
from ...app.event_handlers.showcase_downloader import download_showcases
#curriculog_excel_sheet_generator.classes.app.utils.loading_window 
from ...app.utils.loading_window import LoadingWindow
#curriculog_excel_sheet_generator.classes.report_generator
from ...report_generator import ReportGenerator
from ...excel_input_parser import ExcelInputParser
from ...pandas_helper import PandasHelper
from ...excel_writer import ExcelWriter
def generate_report(api_token, input_excel, window):
    # If input_excel cotains "/output/proposal_overview/current" call download_showcases.download_showcases()
    path = os.path.normpath(input_excel)
    dirs = path.split(os.sep)

    # split the input_excel path into a list
    #Check if proposal_overview and current are in dirs

    if "proposal_overview" in dirs and "current" in dirs :
        download_showcases()
        return
    loading_window = LoadingWindow()
    excel_parser = ExcelInputParser(input_excel)
    excel_parser.parse_workbook()
    excel_parser.get_api_filters()
    report_runner = ReportGenerator(api_token)
    report_runner.actions = excel_parser.actions
    report_runner.get_proposal_list()
    report_runner.get_user_list()
    report_runner.get_all_proposal_field_reports(excel_parser.api_filters)
    process_api_responses(report_runner, excel_parser, input_excel=input_excel)
    

    # Display a message to the user when the API calls are finished
    loading_window.destroy()
    messagebox.showinfo("Report Generated", "The report has been generated.")
    


def process_api_responses(report_runner, excel_parser, input_excel):
  
        
    data_manipulator = PandasHelper(
    proposal_fields_res= report_runner.all_proposal_data,
    proposal_list_res= report_runner.proposal_list,
    user_report_res= report_runner.user_list, 
    fields= excel_parser.fields, 
    grouping_rule= excel_parser.grouping_rule,
    sorting_rules= excel_parser.sorting_rules)
    data_manipulator.concatenate_proposals()


    data_manipulator.transform_column_names()
    data_manipulator.filter_concatenated_proposals(excel_parser.filters)
    data_manipulator.sort_concatenated_proposals(sorting_rules=excel_parser.sorting_rules)
    data_manipulator.get_relevant_columns(excel_parser.fields)
    data_manipulator.get_additional_dataframes()
    writer = ExcelWriter(data_manipulator.concatenated_dataframe, data_manipulator.additional_dataframes, excel_parser.fields, data_manipulator.grouping_rule, report_name=input_excel)
    writer.create_workbook()

    
def on_selection_change(listbox, submit_button):
    if listbox.curselection():
        submit_button.config(state=tk.NORMAL)
    else:
        submit_button.config(state=tk.DISABLED)

# Define a function to get the selected file from the listbox
def get_selected_file(listbox, xlsx_files_dict):
    selected_index = listbox.curselection()
    if selected_index:
        selected_file = listbox.get(selected_index)
        return xlsx_files_dict[selected_file]
    else:
        return None


def validate_api_key(api_key_entry, submit_button):
    if api_key_entry.get().strip() == '':
        submit_button.config(state=tk.DISABLED)
    else:
        submit_button.config(state=tk.NORMAL)
