from .field import Field
from .filter import Filter
from .sorting_rule import SortingRule
from collections import OrderedDict
import pandas as pd
import json
import numpy as np
class PandasHelper:
    
    def concatenate_proposals (self): 
        """Analyzes self.api_responses to form a single Pandas dataframe. Stores the dataframe as concatenated_dataframe."""
        ##Create and store the primary dataframe 'concatenated_proposals'
        self._convert_proposal_field_report_to_pandas_dataframe()
        ##Merge the other api responses (user list & proposal list so we have access to additional data in our dataframe.)
        self._merge_api_responses()
        self.concatenated_dataframe.to_csv('concatenated_dataframe.tsv', sep='\t')
        
        
    def _convert_proposal_field_report_to_pandas_dataframe(self):
        """In the API response for the Curriculog Proposal Field Report, the response nests the fields for a proposal under a list called 'fields'. This function loops over those the api_responses and the nested fields to create a pandas dataframe with a column for each field. If the field, does not exist in given proposal it will be filled with NA."""
        #all_proposals = []
        proposal_field_resp = self.api_responses['/api/v1/report/proposal_field/']
        # for count, ele in enumerate(proposal_field_resp, len(proposal_field_resp)):
        #     all_proposals.append(ele)
        all_keys = set()
        
        fields = []
        # for proposal in proposal_field_resp:
        #     #Nest the proposal_id into the fields, so its column is in the dataframe we make
        #     proposal['fields'].append({
        #         "field_id": 1, #placeholder
        #         "label": "proposal_id",
        #         "rich_text": False,
        #         "tracked": True,
        #         "value": proposal['proposal_id']
        #     })
        #     #Get the fields we need for dataframe
        #     #fields.append(proposal['fields'])
        #     # Add the field labels to our set for use as columns in our pandas dataframe. 
        #     for field in proposal['fields']:
        #         #print(f'FIELD:{field}')
        #         all_keys.add(field['label'])
        # print(f'ALL KEYS: {all_keys}')
        
        
        
        
        # Create a dataframe with all columns 
        # df = pd.DataFrame(columns=all_keys, )
        # # Populate rows  
        # for proposal_field in fields:
        #     df = df.append(proposal_field, ignore_index=True)
        
        #print(df)
            
        # Fill missing values with null
        #df = df.fillna(value=np.nan)
        #self.concatenated_dataframe = df
        
        
        pandas_dict = {}
        for proposal in proposal_field_resp:
            #Nest the proposal_id into the fields, so its column is in the dataframe we make
            proposal['fields'].append({
                "field_id": 1, #placeholder
                "label": "proposal_id",
                "rich_text": False,
                "tracked": True,
                "value": proposal['proposal_id']
            })
            for field in proposal['fields']:
                #FIELDS TO IGNORE BC THEY DONT PLAY NICE IN EXCEL
                if field['label'] not in ['Report']:
                    if field['label'] not in pandas_dict:
                        pandas_dict[field['label']] = []
                    if type(field['value']) is list:
                        
                        pandas_dict[field['label']].append(field['value'][0])
                    else:
                        pandas_dict[field['label']].append(field['value'])
        self.concatenated_dataframe = pd.DataFrame.from_dict(pandas_dict)
        
        self.concatenated_dataframe.to_csv(f'PRIOR TO MERGE.tsv', sep='}')
    
    def _merge_api_responses(self):
        """The primary dataframe 'concatenated_dataframe', is composed of api responses from /api/report/proposal_field. The user may wish to include or filter based-on proposal-related data not in the /api/report/proposal_field response, e.g., Step Name. To counteract this we gather data from the proposal data from other API endpoints and join them to 'concatenated_dataframe'."""
        for api_endpoint, api_response in self.api_responses.items():
            normal = api_endpoint.replace('/', '_')
            self.concatenated_dataframe.to_csv(f'dataframe_for_{normal}.tsv', sep='\t')
            if api_endpoint !=  '/api/v1/report/proposal_field/':
                merge_on = self.proposal_field_merge_key[api_endpoint]
                #print(f'Merging in this API response: {api_response}')
                self.write_json(api_response, api_endpoint.replace('/', '_'))
                api_resp_as_df = pd.DataFrame.from_dict(api_response)
                if 'user_id' in api_resp_as_df.columns:
                    api_resp_as_df.rename(columns={'user_id':'originator_id'}, inplace=True)
                self.concatenated_dataframe = self.merge_dataframes(self.concatenated_dataframe, api_resp_as_df, merge_on)
                # self.concatenated_dataframe.to_csv(f'concatenated_dataframe_{normal}.tsv', sep='\t')
    
    def __init__(self, proposal_list_res, proposal_fields_res, user_report_res, fields:list, sorting_rules, grouping_rule): 
        """proposal_fields_res - The JSON response with proposals and their fields from /api/v1/report/proposal_field/
        proposal_list_res - The JSON response with the list of all proposals in Curriculog and their fields from /api/v1/report/proposal

        fields - A list of Fields which should appear in the dataframes that will ultimately appear in the output Excel workbook.

        sorting_rules - A list of SortingRules which will be used to sort the pandas dataframes prior to writing the output Excel workbook.

        grouping_rule - A string indicating which field to use for creating additional_dataframes from concatenated_dataframes.
        """
        # self.proposal_list = proposal_list
        self.fields = fields
        self.sorting_rules = sorting_rules
        self.grouping_rule = grouping_rule
        self.concatenated_dataframe = pd.DataFrame()
        self.additional_dataframes = []
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
            'url': 'URL'
        }




    def merge_dataframes(self, df1, df2, merge_on):
        """Given two dataframes and a key/column to merge on, merge them and return the resulting dataframe. Used to merge API responses from Curriculog API and allow user access to more fields."""
        return df1.merge(df2, on=merge_on)
    def filter_concatenated_proposals(self, filters:Filter):
        """Accepts a list of Filter instances and filters concatenated_dataframe in Pandas. Stores filtered dataframe as the new value on concatenated_dataframe."""
        for filter_item in filters:
            print(f'Looking for {filter_item.field_name} {filter_item.operator} {filter_item.values}')
            if filter_item.operator == '>':
                self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] > filter_item.values[0]]
            elif filter_item.operator == '>=':
                self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] >= filter_item.values[0]]
            elif filter_item.operator == '<':
                self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] < filter_item.values[0]]
            elif filter_item.operator == '<=':
                self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] <= filter_item.values[0]]
            elif filter_item.operator == '=':
                print('operator is =')
                print(f'{filter_item.field_name} should equal: {filter_item.values[0]}')
                self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] == filter_item.values[0]]
            elif filter_item.operator == '!=':
                self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] != filter_item.values[0]]
            elif filter_item.operator == 'IN':
                self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] in filter_item.values]
            elif filter_item.operator == 'NOT IN':
                self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name]  not in filter_item.values]
            elif filter_item.operator == 'BETWEEN':
                self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name].between(filter_item.values[0], filter_item.values[1])]

    def sort_concatenated_proposals(self, sorting_rules:list[SortingRule]): 
        """Accepts a list of SortingRule instances and sorts**concatenated_dataframe** in Pandas. Sorting is done by the first SortingRule followed by subsequent SortingRules, so SortingRule order matters. Stores sorted dataframe as the new value on concatenated_dataframe."""
        #Keep only the sorting rules that are pertinent to columns in our concatenated dataframe
        sorting_rules = list(filter(lambda sorting_rule: sorting_rule.field_name in self.concatenated_dataframe.columns, sorting_rules))
        self.concatenated_dataframe.to_csv(f'BEFORE_SORT.tsv', sep='\t')
        self.convert_custom_sorts_to_categorical_columns(sorting_rules)
        columns = list(map(lambda sorting_rule: sorting_rule.field_name, sorting_rules))
        #Ascending works for custom bc pd.Categorical data type
        sort_orders = [sorting_rule.sort_order in ['Ascending', 'Custom'] for sorting_rule in sorting_rules]
        print(f'Columns:\n{columns}Sort Order:{sort_orders}')
        self.concatenated_dataframe.sort_values(by=columns, ascending=sort_orders)
        

    def convert_custom_sorts_to_categorical_columns(self, sorting_rules: list[SortingRule]):
        """Accepts a list of sorting rules. For sorting rules with a 'Custom' sort, their corresponding pandas column is converted to a Categorical type to allow for custom sorting."""
        for sorting_rule in sorting_rules:
            #ignore if column does not exist in results
            if sorting_rule.sort_order == 'Custom':
                print(f'The column {sorting_rule.field_name} will be sorted in the following order {sorting_rule.values}')
                self.concatenated_dataframe[sorting_rule.field_name] = pd.Categorical(self.concatenated_dataframe[sorting_rule.field_name], sorting_rule.values)

    def transform_column_names(self):
        """Loops over self.concatenated_dataframe.columns checking for columns that need to be transformed to match the name given in the Input Excel. If found, the column name is transformed to the user-friendly name stored in api_field_names."""
        for col in self.concatenated_dataframe.columns:
            if col in self.api_field_names:
                print(f'Renaming {col} to {self.api_field_names[col]}')
                self.concatenated_dataframe.rename(columns={col:self.api_field_names[col]}, inplace=True)
        

    def get_relevant_columns(self, fields): 
        """
        Filters concatenated_dataframe to include only columns corresponding to the passed in fields. Stores the filtered dataframe as the new value on concatenated_dataframe.

        fields A list of Fields passed in from the ExcelInputParser instance that should appear in the output Excel Workbook."""
        columns = list(map(lambda field: field.field_name, fields))
        #Get which columns aren't in the concatenated dataframe
        missing_columns = list (filter(lambda column: column not in self.concatenated_dataframe.columns, columns))
        print(f'The columns {", ".join(missing_columns)} are not relevant to any of the returned proposals and will not appear in the output Excel workbook. If you believe you have received this message in error please email: jspenc35@utk.edu')
        #Only ask for the columns which actually exist in the concatenated dataframe
        columns = list(filter(lambda column: column in self.concatenated_dataframe.columns, columns))
        self.concatenated_dataframe = self.concatenated_dataframe[columns]

    def get_additional_dataframes(self, field):
        """Using the passed in Field, concatenated_dataframe is filtered to create a new dataframe for each unique value found in the appropriate Field column. Additional dataframes are stored as entries in additional_dataframes. concatenated_dataframe is not mutated."""
        self.get_additional_dataframe_names(field)
        for additional_dataframe_name in self.additional_dataframe_names:
            additional_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[field.field_name] == additional_dataframe_name]
            self.additional_dataframes.append(additional_dataframe)
        

    def get_additional_dataframe_names(self, field:Field): 
        """Using the passed in Field,identify unique values within a column of concatenated_dataframe. Stores unique values as additional_dataframe_names."""
        self.additional_dataframe_names = list(self.concatenated_dataframe[field.field_name].unique())

    def write_json(self, data, file_name):
            """Write out an API response"""
            with open(f'{file_name}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
