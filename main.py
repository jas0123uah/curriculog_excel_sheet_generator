#import classes.proposal_crawler as proposal_crawler
from classes import report_generator, excel_writer, excel_input_parser
import argparse, time
from pprint import pprint
parser = argparse.ArgumentParser()
parser.add_argument('-a', '--api_token', help="The token associated with your API key. Used to pull data from Curriculog. Tokens expire every 25 hours so make sure you have a recent token.")
parser.add_argument('-i', '--input_excel', help="The input excel workbook specifying which proposal fields should appear in the output Excel workbook. Specifies filters and sorting rules for output Excel workbook as well.")
# parser.add_argument('-r', '--report', help="The type of report you are requesting from the Curriculog API.", default= 'proposal_report', choices=['proposal_report'])
parser.add_argument('-er', '--existing_report', nargs='?', help= 'Use this to pull the results for a previously run Curriculog API report. This can be used in cases where the Excel sheet did not format as expected.')
args = parser.parse_args()

excel_parser = excel_input_parser.ExcelInputParser(args.input_excel)
report_runner = report_generator.ReportGenerator(args.api_token, args.existing_report)
try:
    
    if args.existing_report:
        report_runner.get_report_results()
        pass
    else:
        excel_parser.parse_workbook()
        excel_parser.get_api_filters()
        # pprint(vars(excel_parser))
        # for field in excel_parser.fields:
        #     pprint(vars(field))
        # for sorting_rule in excel_parser.sorting_rules:
        #     pprint(vars(sorting_rule))
        report_runner.get_proposal_list()
        report_runner.get_ap_ids()
        report_runner.get_all_proposal_fields(excel_parser.api_filters)
        #report_runner.run_report(args.report)
        #report_runner.get_report_results()
    
    # excel_workbook = excel_writer.ExcelWriter(web_crawl.agenda_name, web_crawl)
    # excel_workbook.create_workbook()
    # excel_workbook.write_main_sheet(web_crawl.analyzed_proposals)
    # colleges = web_crawl.get_colleges_in_proposals()
    # for college in colleges:
    #     proposals_in_college = web_crawl.get_proposals_in_college(college)
    #     excel_workbook.write_additional_sheet(college, proposals_in_college)
    # excel_workbook.save_workbook()

finally:
    time.sleep(5)
