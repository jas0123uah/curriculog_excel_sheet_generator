import os
main_dir = os.getcwd()
output_dir = os.path.join(main_dir, 'output')
os.makedirs(output_dir, exist_ok=True)
api_responses_dir = os.path.join(main_dir, 'reports')
report_template_dir = os.path.join(main_dir, 'inputs')
previous_report_ids_dir = os.path.join(main_dir, 'previous_report_ids')
os.makedirs(previous_report_ids_dir, exist_ok=True)
os.makedirs(report_template_dir, exist_ok=True)
os.makedirs(os.path.join(main_dir, 'output', 'proposal_overview'), exist_ok=True)
os.makedirs(os.path.join(main_dir, 'output', 'proposal_overview', 'current'), exist_ok=True)
os.makedirs(os.path.join(main_dir, 'output', 'proposal_overview', 'previous'), exist_ok=True)
with open(os.path.join(main_dir, '.env'), 'w') as f:
    f.write(f"""PREVIOUS_REPORT_IDS={previous_report_ids_dir}\nNET_ID=''\nPASSWORD=''\nNUM_WEBDRIVERS=1\nMAIN_CURRICULOG_DIR={main_dir}\nTOP_OUTPUT_DIR={output_dir}\nAPI_KEY=''\nAPI_RESPONSES_DIR={api_responses_dir}\nREPORT_TEMPLATES_DIR={report_template_dir}\n""")