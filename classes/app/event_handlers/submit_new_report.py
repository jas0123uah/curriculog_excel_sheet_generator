#from ..curriculog_report_generator import generate_report
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import Text
import sys
from curriculog_excel_sheet_generator.classes.report_generator import ReportGenerator
from  curriculog_excel_sheet_generator.classes.app.utils.print_to_message_box import PrintToMessageBox
from curriculog_excel_sheet_generator.classes.excel_input_parser import ExcelInputParser
from curriculog_excel_sheet_generator.classes.pandas_helper import PandasHelper
from curriculog_excel_sheet_generator.classes.excel_writer import ExcelWriter
def generate_report(api_token, input_excel, window):
    print(f'API TOKEN: {api_token}')

    

     # Create a new window to display the loading bar and messages
    loading_window = tk.Toplevel()
    loading_window.title("Loading...")
    loading_window.geometry("300x200")
    

    textbox=Text(loading_window)
    textbox.pack()

    def redirector(inputStr):
        textbox.insert(tk.INSERT, inputStr)
        textbox.see(tk.END)
        textbox.update()
    sys.stdout.write = redirector

    excel_parser = ExcelInputParser(input_excel)
    excel_parser.parse_workbook()
    excel_parser.get_api_filters()
    report_runner = ReportGenerator(api_token)
    report_runner.get_proposal_list()
    report_runner.get_user_list()
    report_runner.get_all_proposal_field_reports(excel_parser.api_filters)

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
    data_manipulator.get_programs()

    writer = ExcelWriter(data_manipulator.concatenated_dataframe, data_manipulator.additional_dataframes, excel_parser.fields, data_manipulator.grouping_rule)
    writer.create_workbook()

    # Manually write any remaining print messages to the messagebox
    # Reset the standard output
    sys.stdout = sys.__stdout__

    # Close the loading window
    loading_window.destroy()

    # Display a message to the user when the API calls are finished
    messagebox.showinfo("Report Generated", "The report has been generated.")
    
    #generator = report_generator.ReportGenerator(api_token=api_token)

def on_listbox_click(listbox, xlsx_files):
        # Adjust the size of the listbox based on the number of xlsx files found in the directory
        listbox.configure(width=200, height=5*int((len(xlsx_files) * 20) + 20)) # Adjust the size of the listbox based on the number of xlsx files found in the directory
        listbox.configure(font=("Arial", 12, "bold"))
        listbox.configure(bg="#E6E6E6E6" if len(xlsx_files) > 0 else ("Arial", 12, "bold"))
    
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
        print(xlsx_files_dict[selected_file])
        return xlsx_files_dict[selected_file]
    else:
        return None


def validate_api_key(api_key_entry, submit_button):
    if api_key_entry.get().strip() == '':
        submit_button.config(state=tk.DISABLED)
    else:
        submit_button.config(state=tk.NORMAL)
