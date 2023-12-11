#import classes.proposal_crawler as proposal_crawler
from classes import report_generator, excel_writer, excel_input_parser, pandas_helper
import argparse, time
import pandas as pd
from pprint import pprint
parser = argparse.ArgumentParser()
parser.add_argument('-a', '--api_token', help="The token associated with your API key. Used to pull data from Curriculog. Tokens expire every 25 hours so make sure you have a recent token.")
parser.add_argument('-i', '--input_excel', help="The input excel workbook specifying which proposal fields should appear in the output Excel workbook. Specifies filters and sorting rules for output Excel workbook as well.")
parser.add_argument('-plr', '--proposal_list_report_id', nargs='?', help= 'Report ID corresponding to Curriculog Proposal report.')
parser.add_argument('-pfdr', '--proposal_field_difference_report', nargs='?', help= 'Report ID corresponding to Curriculog Proposal Field Difference Report.')

parser.add_argument('-pfrr', '--proposal_field_report_range', nargs='?', help= 'Comma-separated range of report IDs corresponding to Curriculog Proposal Field Reports. This can be used in cases where the Excel sheet did not format as expected./for debugging purposes. For example, to get reports 1-10 enter 1,10')
parser.add_argument('-ur', '--user_report_id', help= 'Report ID corresponding to Curriculog User report.')
args = parser.parse_args()

excel_parser = excel_input_parser.ExcelInputParser(args.input_excel)
excel_parser.parse_workbook()
excel_parser.get_api_filters()

report_runner = report_generator.ReportGenerator(args.api_token, args.proposal_field_report_range)


if args.proposal_list_report_id and  args.proposal_field_report_range:
    report_runner.pull_previous_results(args)
    #report_runner.get_field_differences_report(excel_parser.fields)
else:
    report_runner.get_proposal_list()
    report_runner.get_user_list()
    report_runner.get_all_proposal_field_reports(excel_parser.api_filters)
    #report_runner.get_field_differences_report(excel_parser.fields)


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
data_manipulator.get_relevant_columns(excel_parser.fields)
data_manipulator.concatenated_dataframe.to_excel('test.xlsx')
