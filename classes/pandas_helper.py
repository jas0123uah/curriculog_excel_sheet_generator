from .field import Field
from .filter import Filter
from .flattener import Flattener
from .sorting_rule import SortingRule
from collections import OrderedDict
import pandas as pd
import json, re
import numpy as np
import os
from decouple import config
from pprint import pprint
import logging, sys
# Configure root logger  
logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s |', 
                    filename='log.txt',
                    filemode='a',
                    level=logging.INFO)
logger = logging.getLogger(__name__)




# Log to file
file_handler = logging.FileHandler('log.txt')  
logger.addHandler(file_handler)

# Log to console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


class PandasHelper:
    
    def concatenate_proposals (self): 
        """Analyzes self.api_responses to form a single Pandas dataframe. Stores the dataframe as concatenated_dataframe."""
        ##Create and store the primary dataframe 'concatenated_proposals'
        self._convert_proposal_field_report_to_pandas_dataframe()
        ##Merge the other api responses (user list & proposal list so we have access to additional data in our dataframe.)
        self._merge_api_responses()
        self._transform_college_names()
        self.concatenated_dataframe.to_csv('concatenated_dataframe.tsv', sep='\t')
        
        
    def _convert_proposal_field_report_to_pandas_dataframe(self, save_available_field_names=True):
        """In the API response for the Curriculog Proposal Field Report, the response nests the fields for a proposal under a list called 'fields'. This function loops over those the api_responses and the nested fields to create a pandas dataframe with a column for each field. If the field, does not exist in given proposal it will be filled with NA."""
        proposal_field_resp = self.api_responses['/api/v1/report/proposal_field/']
        pandas_dict = self._get_fields_from_proposals(proposal_field_resp)
       
        pandas_dict = self._get_field_values_from_proposals(pandas_dict, proposal_field_resp)
        
        self.concatenated_dataframe = pd.DataFrame.from_dict(pandas_dict)

        if save_available_field_names is True:
            # Clone concatenated dataframe
            available_fields_df = self.concatenated_dataframe.copy()
            # Transpose columns and rows
            #available_fields_df = available_fields_df.transpose()
            # available_fields_df.to_excel(
            #     os.path.join(config("TOP_OUTPUT_DIR"), "available_fields.xlsx"),
            #     index=False,
            # )
        #self.concatenated_dataframe.to_csv(f'PRIOR TO MERGE.tsv', sep='}')
    def _get_fields_from_proposals(self, proposal_field_resp):
        """Returns a dict of field names that are found in at least one proposal. Values are an empty list."""
        pandas_dict = {}
        ##DETERMINE ALL OF THE DIFFERENT FIELDS A PROPOSAL MAY HAVE. ASSUME THE PROPOSAL_FIELD_RESP HAS DIFFERENT TYPES OF PROPOSALS
        for proposal in proposal_field_resp:
            #Nest the proposal_id into the fields, so its column is in the dataframe we make
            proposal['fields'].append({
                "field_id": 1, #placeholder
                "label": "proposal_id",
                "rich_text": False,
                "tracked": True,
                "value": proposal['proposal_id']
            })
            proposal_list_data = self._find_proposal_in_proposal_list(proposal['proposal_id'])
            if proposal_list_data is None:
                logger.warn(f"A proposal with proposal id {proposal['proposal_id']} was not found in the proposal list api response. This may be because the proposal was launched as the Curriculog script was running! Check https://utk.curriculog.com/proposal:{proposal['proposal_id']}/form and verify the launch time of the proposal roughly coincides with the time you ran this script. If it does not, contact jspenc35@utk.edu for help. If you need data for this proposal you will have to run this script again.")
                continue
            proposal['fields'].append({
                "field_id": 2, #placeholder
                "label": "GR/UG",
                "rich_text": False,
                "tracked": True,
                "value": self._get_level_from_proposal(proposal_list_data)
            })
            proposal['fields'].append({
                "field_id": 3, #placeholder
                "label": "catalog_year",
                "rich_text": False,
                "tracked": True,
                "value": self._get_catalog_year_from_proposal(proposal_list_data)
            })
            proposal['fields'].append({
                "field_id": 4, #placeholder
                "label": "trimmed_ap_name",
                "rich_text": False,
                "tracked": True,
                "value": self._trim_ap_name(proposal_list_data)
            })
            # proposal['fields'].append({
            #     "field_id": 5, #placeholder
            #     "label": "completed_date",
            #     "rich_text": False,
            #     "tracked": True,
            #     "value": proposal_list_data['completed_date']
            # })
            for field in proposal['fields']:
                field_label = field['label']
                #NORMALIZE THE FIELD LABEL/ COMBINE REDUNDANT FIELDS TO A SINGLE COLUMN
                if field_label in self.normalized_api_field_names:
                    field_label = self.normalized_api_field_names[field_label]
                    
                #FIELDS TO IGNORE BC THEY DONT PLAY NICE IN EXCEL
                if field_label not in ['Report', 'Requirements',]:
                    pandas_dict[field_label] = []
            
        return pandas_dict
    def _get_field_values_from_proposals(self, pandas_dict, proposal_field_resp):
        """Loops over proposals and all possible proposal fields. If the proposal has the field its value is appended to the field label in the pandas_dict else np.nan is appended as a  placeholder."""
        pandas_dict['attachments'] = []
        for proposal_number, proposal in enumerate(proposal_field_resp):
            #LOOP OVER ALL POSSIBLE FIELDS A PROPOSAL MAY HAVE
            for field_num, field_label in enumerate(pandas_dict.keys()):
                if field_label == 'attachments':
                    continue
                #print(f'Getting field {field_label} for proposal {proposal_number}')
                field_data = list(filter(lambda proposal_field: proposal_field['label'] == field_label or ( field_label in self.fields_represented_by_normalized_field_name and proposal_field['label'] in self.fields_represented_by_normalized_field_name[field_label]), proposal['fields']))
                #If the field exists in the proposal
                curr_list = pandas_dict[field_label]
                
                ## Will return a list that is at most nested two level deep
                #Should be a list of fields w/ each entry having the attribute 'value'
                all_data_for_field = list(map(lambda datum: [datum['value']], field_data))
    
                flattener = Flattener()
                flattened = flattener.flatten(all_data_for_field)
                #Remove empty strings from list of values
                flattened = list(filter(lambda val: val !='',flattened))
                if field_label != 'proposal_id':
                    
                    data_string = ", ".join(flattened)
                else:
                    data_string = flattened[0]
                if data_string != "":
                    curr_list.append(data_string)
                #The field wasn't found in the given proposal
                else:
                    curr_list.append('')
                pandas_dict[field_label] = curr_list
                # if 'attachments' not in pandas_dict: 
                #     pandas_dict['attachments'] = []
                
            curr_attachments = pandas_dict['attachments']
            proposal_attachments = ", ".join([datum['filename'] for datum in proposal['attachments']])
            curr_attachments.append(proposal_attachments)   
            pandas_dict['attachments'] = curr_attachments
        print(pandas_dict.keys())
        #print(f"Number of attachments: {len(pandas_dict['attachments'])}")
        #print(f"Number of College: {len(pandas_dict['College'])}")
        print(f"Attachments: {pandas_dict['attachments']}")
        print(f"Proposal Names: {pandas_dict['Name of Proposal']}")
        print(f'Curr list: {curr_list}')
        return pandas_dict
        
    
    def _find_proposal_in_proposal_list(self, proposal_id):
        """Returns the data associated with a proposal id in the /api/report/proposal response."""
        proposal_list = self.api_responses['/api/v1/report/proposal']
        match = next((x for x in proposal_list if x['proposal_id'] == proposal_id), None)
        return match
        
    def _merge_api_responses(self):
        """The primary dataframe 'concatenated_dataframe', is composed of api responses from /api/report/proposal_field. The user may wish to include or filter based-on proposal-related data not in the /api/report/proposal_field response, e.g., Step Name. To counteract this we gather data from the proposal data from other API endpoints and join them to 'concatenated_dataframe'."""
        for api_endpoint, api_response in self.api_responses.items():
            normal = api_endpoint.replace('/', '_')
            #self.concatenated_dataframe.to_csv(f'dataframe_for_{normal}.tsv', sep='\t')
            #self.write_json(api_response, api_endpoint.replace('/', '_'))
            if api_endpoint !=  '/api/v1/report/proposal_field/':
                merge_on = self.proposal_field_merge_key[api_endpoint]
                api_resp_as_df = pd.DataFrame.from_dict(api_response)
                #print(f'COLUMNS IN {api_endpoint} {api_resp_as_df.columns}')
                
                if 'user_id' in api_resp_as_df.columns:
                    api_resp_as_df.rename(columns={'user_id':'originator_id'}, inplace=True)
                
                #print(f'api_resp_df {api_resp_as_df.columns}')
                #print(f'concatenated_df {self.concatenated_dataframe.columns}')
                #print(self.concatenated_dataframe)
                self.concatenated_dataframe = self.merge_dataframes(self.concatenated_dataframe, api_resp_as_df, merge_on)
    
    def __init__(self, proposal_list_res, proposal_fields_res, user_report_res, fields:list, sorting_rules, grouping_rule): 
        """proposal_fields_res - The JSON response with proposals and their fields from /api/v1/report/proposal_field/
        proposal_list_res - The JSON response with the list of all proposals in Curriculog and their fields from /api/v1/report/proposal

        fields - A list of Fields which should appear in the dataframes that will ultimately appear in the output Excel workbook.

        sorting_rules - A list of SortingRules which will be used to sort the pandas dataframes prior to writing the output Excel workbook.

        grouping_rule - A string indicating which field to use for creating additional_dataframes from concatenated_dataframes.
        """
        self.fields = fields
        self.sorting_rules = sorting_rules
        self.grouping_rule = grouping_rule
        # print(f'This is proposal_fields_res {proposal_fields_res}')

        self.concatenated_dataframe = proposal_fields_res
        self.additional_dataframes = []
        self.graduate_programs = None
        self.undergraduate_programs = None
        # Use an ordered dict to indicate the order the API responses should be merged in 
        self.api_responses = OrderedDict({
            '/api/v1/report/proposal_field/': proposal_fields_res,
            '/api/v1/report/proposal': proposal_list_res,
            '/api/v1/report/user/': user_report_res,
        })
        self.proposal_field_merge_key = {
            '/api/v1/report/proposal': 'proposal_id',
            '/api/v1/report/user/': 'originator_id'  
        }
        #Lookup to translate API fields to a more friendly column name in the output spreadsheet
        self.api_field_names = {
            'proposal_name': 'Proposal Name',
            'proposal_status': 'Proposal Status',
            'proposal_type': 'Proposal Type',
            'step_name': 'Step Name',
            'url': 'URL',
            'course_number_and_code': 'Course Number and Code',
            'credit_hours': 'Credit Hours',
            'cross_listing': 'Crosslisting',
            'department': 'Department',
            'department_corequisites': 'Department Enforced Corequisites',
            
            'equivalency_chart': 'Equivalency Chart',
            'grading_restriction': 'Grading Restriction',
            'crosslisting_relationship': 'Crosslisting Relationship',
            'prerequisites': 'Prerequisites',
            'will_be_crosslisted': 'Will be Crosslisted',
            'transcript_name': 'Transcript Name',
            'catalog_name': 'Catalog Name',
            'catalog_year': 'Catalog Year',
            'GR/UG': 'GR/UG',
            'ap_name': 'Action',
            'If yes, which Connections category?': 'Connections Categories',
            'trimmed_ap_name': 'Trimmed Action',
            'email': 'Proposal Submitter Email',
            'first_name': 'Proposal Submitter First Name',
            'last_name': 'Proposal Submitter Last Name',
            'is_remote': 'Is Remote',
            'launch_date': 'Proposal Launch Date',
            'If yes, which Vol Core categories?': 'Vol Core Categories',
            'Vol Core categories': 'Vol Core Categories',
            
            'step_start_date': 'Current Step Started (Date)',
            'step_start_date_before' : 'Current Step Started Before (Date)',
            'step_start_date_after': 'Current Step Started After (Date)',
            'step_status': 'Current Step Status',
            
            
        }
        
        #Some fields and their labels represent the same concept (are redundant) - represent these fields with a normalized column name in the pandas df so that their data is in a single column.
        self.normalized_api_field_names = {
            'Course Title (max 100 characters)': 'Course Title',
            'Course Number/Code (max 3 characters)': 'course_number_and_code',
            'Course Number/Code (max 4 characters)': 'course_number_and_code',
            'Course Number/Code (max 4 characters: 3 numerals + optional 1 letter: N, R, S)': 'course_number_and_code',
            'Course Number/Code (max 4 characters: 3 numerals and optional 1 letter: N, R, S)': 'course_number_and_code',
            'Credit Hours': 'credit_hours',
            'Credit Hours (max 4 characters)': 'credit_hours',
            'Credit Hours (max 8 characters)': 'credit_hours',
            'Cross-Listing': 'cross_listing',
            'Cross-Listing?': 'cross_listing',
            'Department (Acalog Hierarchy)': 'department',
            'Department': 'department',
            'Department Enforced (DE) Corequisite(s)': 'department_corequisites',
            'Department Enforced (DE) Corequisite(s):': 'department_corequisites',
            'Equivalency Chart': 'equivalency_chart',
            'Equivalency Table': 'equivalency_chart',
            'Grading Restriction': 'grading_restriction',
            'Grading Restriction (Non-standard Grade Modes)': 'grading_restriction',
            'Grading Restriction (Non-standard Grade Modes) ': 'grading_restriction',
            'Grading Restriction (Other Grade Modes)': 'grading_restriction',
            'Indicate the location on the page where this information will appear. ': 'info_location',
            'Indicate the location on the page(s) where this information will appear. ': 'info_location',
            'List all courses in this crosslisting relationship and note whether primary or secondary': 'crosslisting_relationship',
            'List all courses in this crosslisting relationship and note whether primary or secondary.': 'crosslisting_relationship',
            'Registration Enforced (RE) Prerequisite(s)': 'prerequisites',
            'Registration Enforced (RE) Prerequisite(s):': 'prerequisites',
            'Will this course be crosslisted?': 'will_be_crosslisted',
            'Will this course be cross-listed?': 'will_be_crosslisted',
            'Transcript Name': 'transcript_name',
            'Transcript Name (max 30 characters)': 'transcript_name',
            'Catalog Name': 'catalog_name',
            'Catalog Name (max 100 characters)': 'catalog_name',
            'If yes, which Vol Core categories?': 'Vol Core Categories',
            'Vol Core categories': 'Vol Core Categories',
            'New / Rename Academic Unit?': 'New Academic Unit Name',
            'New / Renamed Academic Unit Name': 'New Academic Unit Name' 
        }
        #Create a reverse of the lookup above
        self.fields_represented_by_normalized_field_name = {}
        for key, value in self.normalized_api_field_names.items():
            if value not in self.fields_represented_by_normalized_field_name:
                self.fields_represented_by_normalized_field_name[value] = [key]
            else:
                self.fields_represented_by_normalized_field_name[value].append(key)

    def merge_dataframes(self, df1, df2, merge_on):
        """Given two dataframes and a key/column to merge on, merge them and return the resulting dataframe. Used to merge API responses from Curriculog API and allow user access to more fields."""
        if df1.empty or df2.empty:
            raise Exception(
                "Dataframe is empty. Does your Current Step Started Before (Date), in your input file use the date you are expecting?")
        
        return df1.merge(df2, on=merge_on)
    def filter_concatenated_proposals(self, filters:Filter):
        """Accepts a list of Filter instances and filters concatenated_dataframe in Pandas. Stores filtered dataframe as the new value on concatenated_dataframe."""
        self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe['Proposal Status'] != 'deleted']
        for filter_item in filters:
            pprint(vars(filter_item))
        #print(list(self.concatenated_dataframe.columns))
        #filters = list(filter(lambda f: f.field_name in self.concatenated_dataframe.columns, filters))
        #print(self.concatenated_dataframe.columns)
        #print(f'Before filtering: {(self.concatenated_dataframe.head())}')
        
        #raise Exception('test')
        for filter_item in filters:
            #pprint(vars(filter_item))
            if filter_item.field_name in self.concatenated_dataframe.columns:
                #print(f'This is filter: {filter_item.field_name} {filter_item.operator} {filter_item.values[0]}')
                if filter_item.operator == '>':
                    print(f'{filter_item.field_name} should be >: {filter_item.values[0]}')
                    self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] > filter_item.values[0]]
                elif filter_item.operator == '>=':
                    print(f'{filter_item.field_name} should be >=: {filter_item.values[0]}')
                    self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] >= filter_item.values[0]]
                elif filter_item.operator == '<':
                    print(f'{filter_item.field_name} should be <: {filter_item.values[0]}')
                    self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] < filter_item.values[0]]
                elif filter_item.operator == '<=':
                    print(f'{filter_item.field_name} should be <=: {filter_item.values[0]}')
                    self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] <= filter_item.values[0]]
                elif filter_item.operator == '=':
                    #comment
                    print(f'{filter_item.field_name} should equal: {filter_item.values[0]}')
                    print(filter_item.values[0])
                    self.concatenated_dataframe = self.concatenated_dataframe.loc[self.concatenated_dataframe[filter_item.field_name] == filter_item.values[0]]
                elif filter_item.operator == 'NOT EQUAL TO':
                    print(f'{filter_item.field_name} should NOT equal: {filter_item.values[0].lower()}')
                    self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] != filter_item.values[0]]
                elif filter_item.operator == 'IN':
                    print(f'{filter_item.field_name} should contain one of the following values: {", ".join(filter_item.values)}')
                    #Filter to have only rows where filter_item.field_name's value is in filter_item.values
                    print(filter_item.values)
                    self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name].apply(lambda x: any(item in str(x) for item in filter_item.values))]
                    #self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] in filter_item.values]
                elif filter_item.operator == 'NOT IN':
                    print(f'{filter_item.field_name} should NOT contain one of the following values: {", ".join(filter_item.values)}')
                    self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name]  not in filter_item.values]
                elif filter_item.operator == 'BETWEEN':
                    print(f'{filter_item.field_name} should be between: {filter_item.values[0]} and {filter_item.values[1]}')
                    self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name].between(filter_item.values[0], filter_item.values[1])]
            else:
                print(f'{filter_item.field_name} is not in the final dataframe. Not applying post-api call filtering for this field')
            
    def sort_concatenated_proposals(self, sorting_rules:list[SortingRule]): 
        """Accepts a list of SortingRule instances and sorts**concatenated_dataframe** in Pandas. Sorting is done by the first SortingRule followed by subsequent SortingRules, so SortingRule order matters. Stores sorted dataframe as the new value on concatenated_dataframe."""
        #Keep only the sorting rules that are pertinent to columns in our concatenated dataframe
        sorting_rules = list(filter(lambda sorting_rule: sorting_rule.field_name in self.concatenated_dataframe.columns, sorting_rules))
        self.convert_custom_sorts_to_categorical_columns(sorting_rules)
        columns = list(map(lambda sorting_rule: sorting_rule.field_name, sorting_rules))
        # Ascending works for custom bc pd.Categorical data type
        sort_orders = [sorting_rule.sort_order in ['Ascending', 'Custom'] for sorting_rule in sorting_rules]
        order_string = "\n".join([sorting_rule.sort_order if sorting_rule.sort_order != 'Custom' else sorting_rule.values for sorting_rule in sorting_rules])
        
        logger.info(f'Data will be sorted by {" then by ".join(columns)} in the following orders respectively:\n {order_string} ')
        self.concatenated_dataframe.sort_values(by=columns, ascending=sort_orders, inplace=True)
        self.concatenated_dataframe.reset_index(drop=True, inplace=True)
        self.concatenated_dataframe.index += 1

    def convert_custom_sorts_to_categorical_columns(self, sorting_rules: list[SortingRule]):
        """Accepts a list of sorting rules. For sorting rules with a 'Custom' sort, their corresponding pandas column is converted to a Categorical type to allow for custom sorting."""
        for sorting_rule in sorting_rules:
            #ignore if column does not exist in results
            if sorting_rule.sort_order == 'Custom':
                #print(f'The column {sorting_rule.field_name} will be sorted in the following order {sorting_rule.values}')
                sort_order = sorting_rule.values.split(",")
                #Explicitly sort blanks last.
                sort_order.append('')
                self.concatenated_dataframe[sorting_rule.field_name] = pd.Categorical(self.concatenated_dataframe[sorting_rule.field_name], sort_order)

    def transform_column_names(self):
        """Loops over self.concatenated_dataframe.columns checking for columns that need to be transformed to match the name given in the Input Excel. If found, the column name is transformed to the user-friendly name stored in api_field_names."""
        for col in self.concatenated_dataframe.columns:
            if col in self.api_field_names:
                self.concatenated_dataframe.rename(columns={col:self.api_field_names[col]}, inplace=True)
        

    def get_relevant_columns(self, fields): 
        """
        Filters concatenated_dataframe to include only columns corresponding to the passed in fields. Stores the filtered dataframe as the new value on concatenated_dataframe.

        fields A list of Fields passed in from the ExcelInputParser instance that should appear in the output Excel Workbook."""
        #Get all columns we are asking for in input excel
        fields_to_keep = list(filter(lambda field: field.dont_return_field == False, fields))
        columns = list(map(lambda field: field.field_name, fields_to_keep))
        
        for field in fields:
            if field.comment_field:
                columns.append(field.comment_field)
        if self.grouping_rule and self.grouping_rule not in columns:
            columns.append(self.grouping_rule)
        #Get which columns user asked for that aren't in the concatenated dataframe so we can warn the user
        missing_columns = list (filter(lambda column: column not in self.concatenated_dataframe.columns, columns))
        if len(missing_columns):
            logger.info(f'The column(s) {", ".join(missing_columns)} are not relevant to any of the returned proposals and will not appear in the output Excel workbook. If you believe you have received this message in error please email: jspenc35@utk.edu')
        
        #Only ask for the columns which actually exist in the concatenated dataframe
        columns = list(filter(lambda column: column in self.concatenated_dataframe.columns, columns))
        self.concatenated_dataframe = self.concatenated_dataframe[columns]

    def get_additional_dataframes(self):
        """Using the self.grouping_rule, concatenated_dataframe is filtered to create a new dataframe for each unique value found in the appropriate Field column. Additional dataframes are stored as entries in additional_dataframes. concatenated_dataframe is not mutated."""
        if self.grouping_rule:
            self.get_additional_dataframe_names(self.grouping_rule)
            for additional_dataframe_name in self.additional_dataframe_names:
                additional_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[self.grouping_rule] == additional_dataframe_name]
                self.additional_dataframes.append({additional_dataframe_name: additional_dataframe})

    def get_additional_dataframe_names(self, field:Field): 
        """Using the passed in Field,identify unique values within a column of concatenated_dataframe. Stores unique values as additional_dataframe_names."""
        self.additional_dataframe_names = list(self.concatenated_dataframe[field].unique())

    # def get_programs(self):
    #     """Filter concatenated_proposals to identify only those that are for a Graduate or Undergraduate program. Stores programs under graduate_programs and undergraduate_programs, respectively."""
    #     print( self.concatenated_dataframe.columns)
    #     self.undergraduate_programs = self.concatenated_dataframe[(self.concatenated_dataframe['GR/UG'] == 'UG') &  (self.concatenated_dataframe['Proposal Type'] == 'program') &  (self.concatenated_dataframe['completed_date'].notnull())]
    #     self.graduate_programs = self.concatenated_dataframe[(self.concatenated_dataframe['GR/UG'] == 'GR') &  (self.concatenated_dataframe['Proposal Type'] == 'program')]
    def write_json(self, data, file_name):
            """Write out an API response"""
            with open(f'{file_name}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
    def _get_catalog_year_from_proposal(self, proposal):
        """Parse the ap_name to get the catalog year for a given proposal."""
        proposal_action = proposal['ap_name']
        pattern = r"(20\d{2})-(20\d{2})\s"

        match = re.search(pattern, proposal_action)
        if match:
            return f'{match.group(1)}-{match.group(2)}'
        return ''

    def _get_level_from_proposal(self, proposal):
        """Parse the ap_name to get the catalog year for a given proposal. Return empty string if UG or GR not found."""
        proposal_action = proposal['ap_name']
        words = proposal_action.split(' ')
        if "GR" in words:
            return "GR"
        elif "UG" in words:
            return 'UG'
        else:
            return ""
    def _trim_ap_name(self, proposal):
        """Removes text up to and including, GR or UG from proposal action"""
        proposal_action = proposal['ap_name']
        words = proposal_action.split(' ')
        if "GR" in words:
            i = words.index("GR")
            return " ".join(words[i+1:])
        elif "UG" in words:
            i = words.index("UG")
            return " ".join(words[i+1:])
        else:
            return proposal_action
    
    def _transform_college_names(self):
        """Transforms college names to match shortened named. Shortened name is what is returned when the user asks for a college name."""
        college_lookup = {
            'College of Arts and Sciences' :'CAS',
            'Herbert College of Agriculture':'HCA',
            'Howard H. Baker Jr. School of Public Policy and Public Affairs':'HBS',
            'Tickle College of Engineering': 'TCE',
            'College of Architecture and Design': 'CAD',
            'College of Communication and Information': 'CCI',
            'College of Education, Health, and Human Sciences': 'CEHHS',
            'College of Emerging and Collaborative Studies': 'CECS',
            'College of Law': 'CoL',
            'College of Nursing': 'CoN',
            'College of Social Work': 'CSW',
            'College of Music': 'CoM',
            'College of Veterinary Medicine': 'VetMed',
            'Haslam College of Business': 'HCB',
            'Reserve Officers Training Corps (ROTC)': 'ROTC',
        }
        for old_name, new_name in college_lookup.items():
            self.concatenated_dataframe.replace(old_name, new_name, inplace=True)
