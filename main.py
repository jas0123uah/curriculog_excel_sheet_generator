#import classes.proposal_crawler as proposal_crawler

from classes import report_generator, excel_writer, excel_input_parser, pandas_helper, showcase_downloader 
import argparse, shutil, os, sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--api_token', help="The token associated with your API key. Used to pull data from Curriculog. Tokens expire every 25 hours so make sure you have a recent token.")
parser.add_argument('-i', '--input_excel', help="The input excel workbook specifying which proposal fields should appear in the output Excel workbook. Specifies filters and sorting rules for output Excel workbook as well.")

parser.add_argument('-plr', '--proposal_list_report_id', nargs='?', help= 'Report ID corresponding to Curriculog Proposal report.')


parser.add_argument('-pfrr', '--proposal_field_report_range', nargs='?', help= 'Comma-separated range of report IDs corresponding to Curriculog Proposal Field Reports. This can be used in cases where the Excel sheet did not format as expected./for debugging purposes. For example, to get reports 1-10 enter 1,10')
parser.add_argument('-ur', '--user_report_id', help= 'Report ID corresponding to Curriculog User report.')
parser.add_argument('-d', '--debug_mode', action=argparse.BooleanOptionalAction, help="Flag to indicate if API responses from Curriculog should be stored locally under reports directory. Useful when debugging or adding new features.")
parser.add_argument('-gsc', '--get_showcases', action=argparse.BooleanOptionalAction, help="Flag to indicate if program showcase docs should be created for each college.")
parser.add_argument('-n', '--netid', help= 'The NetID to log into Curriculog to retrieve program showcases.', required=False)
parser.add_argument('-p', '--password', help= 'The password to log into Curriculog to retrieve program showcases.', required=False)
parser.add_argument('-ap', '--get_ap_names', action='store_true', help= 'Pull the different  apIds & ap names for the available Curriculog proposals.', required=False)
parser.add_argument('-f', '--field_report',  help= 'Pull the proposals for a specific ap_id.', required=False)

args = parser.parse_args()

os.makedirs('reports', exist_ok=True)
report_runner = report_generator.ReportGenerator(args.api_token)
if args.get_ap_names is not False:
    report_runner.get_ap_names()
    sys.exit()

if args.field_report:
    report_runner.get_all_proposal_field_reports(ap_id=args.field_report)
    sys.exit()
excel_parser = excel_input_parser.ExcelInputParser(args.input_excel)
excel_parser.parse_workbook()
excel_parser.get_api_filters()

#report_runner.refresh_api_token()

attachments = report_runner.get_attachments()

# with open('reports/attachments.pdf', 'wb') as f:
#     f.write(attachments)
# sys.exit()
if args.proposal_list_report_id and  args.proposal_field_report_range:
    report_runner.pull_previous_results(args)
else:
    report_runner.get_proposal_list()
    report_runner.get_user_list()
    report_runner.get_all_proposal_field_reports(excel_parser.api_filters)


data_manipulator = pandas_helper.PandasHelper(
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
print(data_manipulator.undergraduate_programs['URL'])
if args.get_showcases:
    data_manipulator.get_programs()
    downloader = showcase_downloader.ShowcaseDownloader(data_manipulator.undergraduate_programs, data_manipulator.graduate_programs, args)
    downloader.download_showcases()
#print(data_manipulator.undergraduate_programs['URL'])


data_manipulator.get_relevant_columns(excel_parser.fields)
data_manipulator.get_additional_dataframes()

data_manipulator.concatenated_dataframe.to_excel('test.xlsx')

writer = excel_writer.ExcelWriter(data_manipulator.concatenated_dataframe, data_manipulator.additional_dataframes, excel_parser.fields, data_manipulator.grouping_rule, report_name=Path(args.input_excel).stem)
writer.create_workbook()
if args.debug_mode == False:
    shutil.rmtree('./reports')
