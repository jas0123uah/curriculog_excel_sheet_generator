import requests, json, re, time, os
import datetime
from pprint import pprint
from .field import Field
import logging, sys

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
    
    def get_user_list(self):
        """Wrapper function for handling API call to'/api/v1/report/user'"""
        self.user_list = self.run_report(api_endpoint='/api/v1/report/user/', report_type='USER LIST')
        return self.user_list
        
    def get_all_proposal_field_reports(self, api_filters):
        """Wrapper function for handling API call to '/api/v1/report/proposal_field'. Loops over self.ap_ids to gather proposal fields for all proposals. Stores API responses in all_proposal_data. """
        report_ids = []
        all_proposals_w_data = []
        self.get_ap_ids()
        for ap_id in self.ap_ids:
            logger.info(f'Submitting Proposal Field Report request for ap_id {ap_id}')
            
            request_params = {'ap_id': ap_id}
            request_params.update(api_filters)
            request_params = json.dumps(request_params)
            
            report_id = self.run_report(api_endpoint='/api/v1/report/proposal_field/', request_params=request_params, report_type='PROPOSAL FIELD', wait_for_results=False )
            report_ids.append(report_id)

        for report_id in report_ids:
            proposals_w_data = self.get_report_results(report_id)
            all_proposals_w_data = [*all_proposals_w_data, *proposals_w_data]
        
        self.all_proposal_data = all_proposals_w_data
    ######## BASE-LEVEL FUNCTIONS USED BY WRAPPER FUNCTIONS TO INTERACT WITH THE API ########
    def run_report(self, *, api_endpoint, request_params= None, wait_for_results=True, report_type, ):
        """Sends POST request to Curriculog api_endpoint. Report_type prints a helpful message for retrieving the report for debugging purposes."""        
        url = f'{self.base_url}{api_endpoint}'
        if request_params: 
            response = requests.post(url=url, headers=self.headers, data=request_params, allow_redirects=True)
        else:
            response = requests.post(url=url, headers=self.headers, allow_redirects=True)
        #pprint(vars(response))
        report_id = response.json()['report_id']
        logger.info(f'{report_type} IS UNDER REPORT ID: {report_id}')
        if wait_for_results:
            results = self.get_report_results(report_id)
            return results
        return report_id
    
    def get_report_results(self, report_id): 
        """Given a report_id call /api/v1/report/result/{report_id} to get the results for a Curriculog report."""
        logger.info(f'Pulling results for report id {report_id}.')
        if os.path.exists(f'./reports/{report_id}.json'):
            with open(f'./reports/{report_id}.json', 'r', encoding='utf-8', errors="ignore") as f:
                data = f.read()
                return json.loads(data)
        api_endpoint = f'/api/v1/report/result/{report_id}'
        url = f'{self.base_url}{api_endpoint}'
        response = requests.get(url=url, headers=self.headers, allow_redirects=True)
        meta = response.json()['meta']

        #print(f'META:{meta}')
        #print(response.json())
        no_results = 'error' in meta and 'message' in meta['error'] and 'No results' in meta['error']['message']
        if no_results:
            remaining_num_attempts = 30
            remaining_num_attempts -= 1
            while no_results and remaining_num_attempts:
                now = datetime.datetime.now()
                sixty_secs_from_now = now + datetime.timedelta(0, 60)
                logger.info(f"No results for report id {report_id}. Waiting 60 seconds and trying again at {sixty_secs_from_now.strftime('%I:%M:%S')}. {remaining_num_attempts} attempts remaining.")
                time.sleep(60)
                response = requests.get(url=url, headers=self.headers, allow_redirects=True)
                meta = response.json()['meta']
                no_results = 'error' in meta and 'message' in meta['error'] and 'No results' in meta['error']['message']
        
        if meta['total_results'] != meta['results_current_page']:
            err = f'There are {meta["total_results"]} total results and only {meta["results_current_page"]} results are on the current page. Please contact jspenc35@utk.edu with this error and provide the report_id {report_id}.'
            logger.error(err)
            raise Exception(err)
        self.write_json(response.json()['results'], f'./reports/{report_id}')
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
        ap_ids = []
        for proposal in self.proposal_list:
            if proposal['ap_id'] not in ap_ids:
                ap_ids.append(proposal['ap_id'])
        self.ap_ids = ap_ids
        return ap_ids

    def pull_previous_results(self, args):
        """Wrapper function that makes it possible to recreate previous runs of the script."""
        ### Pulling for /api/report/proposal here
        self.proposal_list = self.get_report_results(args.proposal_list_report_id) 
        
        ### Pulling for /api/report/user here
        self.user_list = self.get_report_results(args.user_report_id) 
        
        ### Pulling for /api/report/proposal_field here
        report_id_range = args.proposal_field_report_range.split(',')
        
        all_results = []
        for report_id in range(int(report_id_range[0].strip()), int(report_id_range[1].strip())+1):
            results = self.get_report_results(report_id)
            all_results = [*all_results, *results]
        self.all_proposal_data = all_results

    
    def write_json(self, data, file_name):
        """Write out an API response"""
        with open(f'{file_name}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
