#import classes.proposal_crawler as proposal_crawler
from classes import report_generator, excel_writer, excel_input_parser, pandas_helper
import argparse, time
from pprint import pprint
parser = argparse.ArgumentParser()
parser.add_argument('-a', '--api_token', help="The token associated with your API key. Used to pull data from Curriculog. Tokens expire every 25 hours so make sure you have a recent token.")
parser.add_argument('-i', '--input_excel', help="The input excel workbook specifying which proposal fields should appear in the output Excel workbook. Specifies filters and sorting rules for output Excel workbook as well.")
parser.add_argument('-er', '--existing_report_ids', nargs='?', help= 'Comma-separated range of report IDs corresponding to Curriculog API reports to pull.This can be used in cases where the Excel sheet did not format as expected./for debugging purposes. For example, to get reports 1-10 enter 1,10')
args = parser.parse_args()

excel_parser = excel_input_parser.ExcelInputParser(args.input_excel)
excel_parser.parse_workbook()
excel_parser.get_api_filters()

report_runner = report_generator.ReportGenerator(args.api_token, args.existing_report_ids)


if args.existing_report_ids:
    report_id_range = args.existing_report_ids.split(',')
    all_results = []
    for report_id in range(int(report_id_range[0].strip()), int(report_id_range[1].strip())+1):
        print(f'Pulling results for report id {report_id}.')
        results = report_runner.get_report_results(report_id)
        all_results = [*all_results, *results]
    report_runner.all_proposal_data = all_results
else:
    report_runner.get_proposal_list()
    report_runner.get_ap_ids()
    report_runner.get_all_proposal_fields(excel_parser.api_filters)


data_manipulator = pandas_helper.PandasHelper(
    proposal_list= report_runner.all_proposal_data, 
    fields= excel_parser.fields, 
    grouping_rule= excel_parser.grouping_rule,
    sorting_rules= excel_parser.sorting_rules)
data_manipulator.filter_concatenated_proposals(excel_parser.filters)
data_manipulator.sort_concatenated_proposals(sorting_rules=excel_parser.sorting_rules)
data_manipulator.get_relevant_columns(excel_parser.gr)
