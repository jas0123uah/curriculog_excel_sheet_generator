import tkinter as tk
from tkinter import messagebox
import os, json
from ..event_handlers import generate_report, process_api_responses
from ..event_handlers.showcase_downloader import download_showcases
from ...report_generator import ReportGenerator
from ...excel_input_parser import ExcelInputParser
from ...app.utils import LoadingWindow, get_current_proposal_overview_report
from pathlib import Path
from decouple import config
def build_new_report_window():
    def use_last_api_calls_callback(input_excel, ):
        normalized_path = os.path.normpath(input_excel)
        if  r'\output\proposal_overview\current' in  normalized_path or  "/output/proposal_overview/current" in normalized_path:
            download_showcases()
            return
        input_excel = get_selected_file(listbox, xlsx_files_dict)
        excel_parser = ExcelInputParser(input_excel)
        excel_parser.parse_workbook()
        excel_parser.get_api_filters()
        output_file = os.path.join(config('TOP_OUTPUT_DIR'), Path(input_excel).stem, 'current')
        prev_report_id_file = config('PREVIOUS_REPORT_IDS')+'previous_report_ids.json'
        if os.path.exists(prev_report_id_file) == False:
            messagebox.showerror(title="Error", message=f"{prev_report_id_file} does not exist. This file contains the previous report IDs. Please generate a new report.")
        report_generator = ReportGenerator(api_token=api_key_entry.get())
        report_generator.actions = excel_parser.actions
        # Read in prev_report_id_file
        with open(prev_report_id_file) as f:
            data = json.load(f)
        report_generator.pull_previous_results(data)
        process_api_responses(report_generator, input_excel= input_excel, excel_parser=excel_parser)
        messagebox.showinfo("Report Generated", f"Report created successfully under: {output_file}")

    
    def on_selection_change(listbox, submit_button, api_key_entry):
        if listbox.curselection() and api_key_entry.get().strip() != '':
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
    

    def validate_api_key():
        if api_key_entry.get().strip() == '' or len(listbox.curselection()) == 0:
            submit_button.config(state=tk.DISABLED)
        else:
            submit_button.config(state=tk.NORMAL)

    # Create a new window
    new_window = tk.Toplevel()
    new_window.wm_title( "New Report")
    new_window.geometry("300x350")

    # Create a frame to hold the title label
    title_frame = tk.Frame(new_window)
    title_frame.pack(pady=10)

    # Create a text label for the title
    title_label = tk.Label(title_frame, text="Reports", font=("Arial", 16, "bold"))
    title_label.pack(side=tk.LEFT)

    directory = r'C:\Users\jspenc35\projects\curriculog_excel_sheet_generator\inputs'
    
    # Get the absolute path of the xlsx files in the directory
    xlsx_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.xlsx')]

    xlsx_files_transformed = [f for f in os.listdir(directory) if f.endswith('.xlsx')]


    # Add the current proposal overview report if it exists
    current_proposal_overview_report = get_current_proposal_overview_report()

    if current_proposal_overview_report is not None:
        xlsx_files.append(current_proposal_overview_report)


    # #Make the Filenames Title Case
    xlsx_files_transformed = [f.title() for f in xlsx_files_transformed]

    # #Remove their extension
    xlsx_files_transformed = [os.path.splitext(f)[0] for f in xlsx_files_transformed]

    # #Remove UnderScores
    xlsx_files_transformed = [f.replace("_", " ") for f in xlsx_files_transformed]

    # Add Download Showcases if there is a current proposal overview report
    if current_proposal_overview_report is not None:
        xlsx_files_transformed.append('Download Showcases')

    # Create a dict of the transformed filenames
    xlsx_files_dict = dict(zip(xlsx_files_transformed, xlsx_files))

    # Create a listbox to display the filenames
    listbox = tk.Listbox(new_window, width=100)
    listbox.pack(pady=10)
    listbox.bind("<<ListboxSelect>>", lambda event: on_selection_change(listbox, submit_button, api_key_entry))


    # Create a frame to hold the API key label and entry field
    api_key_frame = tk.Frame(new_window)
    api_key_frame.pack(pady=10, padx=(0, 10))

    # Create a label and entry field for the API key
    api_key_label = tk.Label(api_key_frame, text="API Key:")
    api_key_label.grid(row=0, column=0)
    api_key_entry = tk.Entry(api_key_frame)
    api_key = config('API_KEY', default='')
    api_key_entry.insert(0, api_key)
    api_key_entry.grid(row=0, column=1)
    api_key_entry.bind("<KeyRelease>", lambda event: validate_api_key())  # Bind the validation function to the KeyRelease event


    # Create a checkbox before the Submit button that reads "Use Last API Calls"
    use_last_api_calls_var = tk.BooleanVar()
    use_last_api_calls_checkbox = tk.Checkbutton(new_window, text="Use Last API Calls", variable=use_last_api_calls_var)
    use_last_api_calls_checkbox.pack(anchor="w", side="left", padx=10, pady=10)

    # Create a submit button
    submit_button = tk.Button(new_window, text="Submit", state=tk.DISABLED, command=lambda: use_last_api_calls_callback(input_excel= get_selected_file(listbox, xlsx_files_dict)) if use_last_api_calls_var.get() == True else  generate_report(api_key_entry.get(), input_excel= get_selected_file(listbox, xlsx_files_dict), window=new_window))
    submit_button.pack(pady=10)

    # Add the filenames to the listbox
    for filename in xlsx_files_transformed:
        listbox.insert(tk.END, filename)
    
    #Todo: Find a better equation
    listbox.configure(width=30, height=1.2*int((len(xlsx_files)) + 10)) # Adjust the size of the listbox based on the number of xlsx files found in the directory
    listbox.configure(font=("Arial", 12, "bold"))
    listbox.configure(bg="#E6E6E6E6" if len(xlsx_files) > 0 else ("Arial", 12, "bold"))

    # Start the main loop of the new window
    new_window.mainloop()
