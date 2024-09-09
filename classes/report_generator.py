import requests, json, re, time, os
import datetime
from pprint import pprint
from .field import Field
import logging, sys
from decouple import config
import configparser
import concurrent.futures

# Configure root logger  
logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s |', 
                    filename='log.txt',
                    filemode='a',
                    level=logging.INFO)
logger = logging.getLogger()



# Log to file
file_handler = logging.FileHandler('log.txt')  
logger.addHandler(file_handler)

# Log to console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


class ReportGenerator:
    def __init__(self, api_token) -> None:
        self.api_token = api_token
        self.base_url = 'https://utk.curriculog.com'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        }
        self.all_proposal_data = []
        self.proposal_list_report_id = None
        self.user_report_id = None
        self.actions = []
        self.report_ids = []
        #Default empty list for api/v1/reports/user/ report
        self.user_list = []
        
        ##Used to identify field ids to ask for in proposal_diff report
        self.normalized_field_names = {
            'Course Number/Code': ['Course Number/Code (max 3 characters)',
                                'Course Number/Code (max 4 characters: 3 numerals + optional 1 letter: N, R, S)',
                                'Course Number/Code (max 4 characters: 3 numerals and optional 1 letter: N, R, S)']
        }
        
        ## {
            # The 'normalized' field name used in the input Excel workbook: ['Duplicate Curriculog Field Label representing the same concept', 'Represents the same concept']
        ## }
    ######## WRAPPER FUNCTIONS W/ USER-FRIENDLY NAMES FOR RUNNING CURRICULOG API REPORTS ########
    def get_proposal_list(self):
        """Wrapper function for handling API call to'/api/v1/report/proposal/'"""
        self.proposal_list = self.run_report(api_endpoint='/api/v1/report/proposal/', report_type='PROPOSAL LIST')
        return self.proposal_list
    
    def get_ap_names(self):
        """Wrapper function for getting a proposal list and looping over it to get all ap_names & their corresponding ap_id."""
        self.get_proposal_list()
        lookup = {}
        for proposal in self.proposal_list:
            ap_id = proposal['ap_id']
            ap_name = proposal['ap_name']
            lookup[ap_name] = ap_id
            logger.info(f'Retrieved ap_id: {ap_id}, ap_name: {ap_name}')
            #self.ap_ids.append(ap_id)
        with open('ap_names.csv', 'w') as f:
            #Write dictionary to file with one row per key-value pair
            f.write(f'AP Name, AP ID\n')
            for key, value in lookup.items():
                f.write(f'{key},{value}\n')

        #return self.ap_ids
    
    def get_user_list(self):
        """Wrapper function for handling API call to'/api/v1/report/user'"""
        self.user_list = self.run_report(api_endpoint='/api/v1/report/user/', report_type='USER LIST')
        return self.user_list
        
    def get_attachments(self, report_id=None):
        """Wrapper function for handling API call to '/api/v1/attachments'. Returns a list of all attachments for the report."""
        if report_id is None:
            attachments_list = self.run_report(api_endpoint='/api/v1/attachments/3', report_type='ATTACHMENTS')
            return attachments_list
        else:
            attachments = self.run_report(api_endpoint=f'/api/v1/attachments/{report_id}')
    def get_all_proposal_field_reports(self, api_filters = {}, ap_id=None):
        """Wrapper function for handling API call to '/api/v1/report/proposal_field'. Loops over self.ap_ids to gather proposal fields for all proposals. Stores API responses in all_proposal_data. """
        all_proposals_w_data = []
        if ap_id is None:
            self.get_ap_ids()
        else:
            self.ap_ids = [ap_id]


        for ap_id in self.ap_ids:
            print(f'Submitting Proposal Field Report request for ap_id {ap_id}')
            
            request_params = {'ap_id': ap_id}
            for key, value in api_filters.items():
                if type(value) is list:
                    api_filters[key] = value[0]
            request_params.update(api_filters)
            request_params = json.dumps(request_params)
            
            report_id = self.run_report(api_endpoint='/api/v1/report/proposal_field/', request_params=request_params, report_type='PROPOSAL FIELD', wait_for_results=False )
            self.report_ids.append(report_id)
        
        
        self.write_report_ids()

        for report_id in self.report_ids:
            proposals_w_data = self.get_report_results(report_id)
            all_proposals_w_data = [*all_proposals_w_data, *proposals_w_data]
        
        #print(f'All Proposals Data: {all_proposals_w_data}')
        self.all_proposal_data = all_proposals_w_data
    ######## BASE-LEVEL FUNCTIONS USED BY WRAPPER FUNCTIONS TO INTERACT WITH THE API ########
    def run_report(self, *, api_endpoint, request_params= None, wait_for_results=True, report_type, ):
        """Sends POST request to Curriculog api_endpoint. Report_type prints a helpful message for retrieving the report for debugging purposes."""        
        url = f'{self.base_url}{api_endpoint}'
        
        if report_type == 'ATTACHMENTS':
            response = requests.get(url=url, headers=self.headers, allow_redirects=True)
            return response._content
        elif request_params: 
            response = requests.post(url=url, headers=self.headers, data=request_params, allow_redirects=True)
        else:
            response = requests.post(url=url, headers=self.headers, allow_redirects=True)
        #pprint(vars(response))
        report_id = response.json()['report_id']
        if report_type == 'USER LIST':
            self.user_report_id = report_id
        elif report_type == 'PROPOSAL LIST':
            self.proposal_list_report_id = report_id
        print(f'{report_type} IS UNDER REPORT ID: {report_id}')
        if wait_for_results:
            results = self.get_report_results(report_id)
            return results
        return report_id
    
    def get_report_results(self, report_id): 
        """Given a report_id call /api/v1/report/result/{report_id} to get the results for a Curriculog report."""
        print(f'Pulling results for report id {report_id}.')
        #logger.info(f'Pulling results for report id {report_id}.')
        if os.path.exists(f'./reports/{report_id}.json'):
            with open(f'./reports/{report_id}.json', 'r', encoding='utf-8', errors="ignore") as f:
                data = f.read()
                return json.loads(data)
        api_endpoint = f'/api/v1/report/result/{report_id}'
        url = f'{self.base_url}{api_endpoint}'
        response = requests.get(url=url, headers=self.headers, allow_redirects=True)
        #print(response.json())
        meta = response.json()['meta']

        #print(f'META:{meta}')
        no_results = 'error' in meta and 'message' in meta['error'] and 'No results' in meta['error']['message']
        if no_results:
            remaining_num_attempts = 5
            remaining_num_attempts -= 1
            while no_results and remaining_num_attempts:
                now = datetime.datetime.now()
                sixty_secs_from_now = now + datetime.timedelta(0, 60)
                #print(meta['error'])
                print(f'No results for report id {report_id}. Waiting 60 seconds and trying again at {sixty_secs_from_now.strftime("%I:%M:%S")}. {remaining_num_attempts} attempts remaining.')
                #logger.info(f"No results for report id {report_id}. Waiting 60 seconds and trying again at {sixty_secs_from_now.strftime('%I:%M:%S')}. {remaining_num_attempts} attempts remaining.")
                time.sleep(60)
                response = requests.get(url=url, headers=self.headers, allow_redirects=True)
                #print(response.json())
                meta = response.json()['meta']
                #print(meta)
                no_results = 'error' in meta and 'message' in meta['error'] and 'No results' in meta['error']['message']
                remaining_num_attempts -= 1
        
        if no_results:
            print(f'NO RESULTS FOR REPORT ID  {report_id}. SKIPPING')
            return []
        if meta['total_results'] != meta['results_current_page']:
            err = f'There are {meta["total_results"]} total results and only {meta["results_current_page"]} results are on the current page. Please contact jspenc35@utk.edu with this error and provide the report_id {report_id}.'
            logger.error(err)
            raise Exception(err)
        # if config('API_REPONSES_DIR') does not exist, create it
        if not os.path.exists(config('API_REPONSES_DIR')):
            os.makedirs(config('API_REPONSES_DIR'))
        directory = config('API_REPONSES_DIR')
        self.write_json(response.json()['results'], directory + report_id)
        return response.json()['results']
    def refresh_api_token(self):
        """Refreshes the Curriculog API token to prevent token expiration errors."""
        logger.info('Refreshing API token.')
        api_endpoint = f'/api/v1/token/refresh/'
        url = f'{self.base_url}{api_endpoint}'
        response = requests.get(url=url, headers=self.headers, allow_redirects=True)
        logger.info(response)
        
    ######## MISC FUNCTIONS ########
    def get_ap_ids(self): 
        """Loops over proposal_list to return a unique list of ap_ids."""
        ap_id_lookup = {}
        for proposal in self.proposal_list:
            ap_id = proposal['ap_id']
            proposal_name = proposal['ap_name']
            ap_id_lookup[proposal_name] = ap_id
        if len(self.actions) == 0:
            self.ap_ids = list(ap_id_lookup.values())
        else:
            # Pull the values from ap_id lookup that have keys in self.actions
            self.ap_ids = [ap_id_lookup[action] for action in self.actions]
        return self.ap_ids

    def pull_previous_results(self, args):
        """Wrapper function that makes it possible to recreate previous runs of the script."""
        ### Pulling for /api/report/proposal here
        self.proposal_list = self.get_report_results(args['proposal_list_report_id']) 
        
        ### Pulling for /api/report/user here
        self.user_list = self.get_report_results(args['user_list_report_id'])
        
        ### Pulling for /api/report/proposal_field here
        report_id_range = args['proposal_field_report_range'].split(',')
        
        all_results = []
        for report_id in range(int(report_id_range[0].strip()), int(report_id_range[1].strip())+1):
            results = self.get_report_results(str(report_id))
            if results is not None:
                all_results = [*all_results, *results]

        self.all_proposal_data = all_results

    
    def write_json(self, data, file_name):
        """Write out an API response"""
        with open(r"{}".format(f"{file_name}.json"), 'w', encoding='utf-8')as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def write_report_ids(self):
        """Write out report ids for self.report_ids, self.proposal_list_report_id, and self.user_report_id. to allow recreation of previous runs of the script."""
        data = {'proposal_field_report_range': f"{self.report_ids[0]},{self.report_ids[-1]}", 'proposal_list_report_id': self.proposal_list_report_id, 'user_list_report_id': self.user_report_id}
        # Check if config("PREVIOUS_REPORT_IDS") exists. If it does not, create it.
        if not os.path.exists(config("PREVIOUS_REPORT_IDS")):
            os.makedirs(config("PREVIOUS_REPORT_IDS"))
        self.write_json(data,f'{config("PREVIOUS_REPORT_IDS")+"previous_report_ids"}')
