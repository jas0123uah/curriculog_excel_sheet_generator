import requests, json
from pprint import pprint
class ReportGenerator:
    def __init__(self, api_token, report_id = None) -> None:
        self.api_token = api_token
        self.base_url = 'https://utk.curriculog.com'
        self.report_id = report_id
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        }
        self.all_proposal_data = []
        #Default empty list for api/v1/reports/user/ report
        self.user_list = []
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
        all_proposals_w_data = []
        self.get_ap_ids()
        print(self.ap_ids)
        for ap_id in self.ap_ids:
            print(f'Getting proposal fields for ap_id {ap_id}')
            
            request_params = {'ap_id': ap_id}
            request_params.update(api_filters)
            request_params = json.dumps(request_params)
            
            proposals_w_data = self.run_report(api_endpoint='/api/v1/report/proposal_field/', request_params=request_params, report_type='PROPOSAL FIELD' )

            all_proposals_w_data = [*all_proposals_w_data, *proposals_w_data]
        self.all_proposal_data = all_proposals_w_data
        self.write_json(all_proposals_w_data, 'proposals')
            

    
    ######## BASE-LEVEL FUNCTIONS USED BY WRAPPER FUNCTIONS TO INTERACT WITH THE API ########
    def run_report(self, *, api_endpoint, request_params= None, report_type, ):
        """Sends POST request to Curriculog api_endpoint. Report_type prints a helpful message for retrieving the report for debugging purposes."""        
        url = f'{self.base_url}{api_endpoint}'
        if request_params: 
            response = requests.post(url=url, headers=self.headers, data=request_params, allow_redirects=True)
        else:
            response = requests.post(url=url, headers=self.headers, allow_redirects=True)
        report_id = response.json()['report_id']
        print(f'{report_type} IS UNDER REPORT ID: {report_id}')
        results = self.get_report_results(report_id)
        return results
    
    def get_report_results(self, report_id): 
        """Given a report_id call /api/v1/report/result/{report_id} to get the results for a Curriculog report."""

        api_endpoint = f'/api/v1/report/result/{report_id}'
        url = f'{self.base_url}{api_endpoint}'
        response = requests.get(url=url, headers=self.headers, allow_redirects=True)
        meta = response.json()['meta']

        
        if meta['total_results'] != meta['results_current_page']:
            err = f'There are {meta["total_results"]} total results and only {meta["results_current_page"]} results are on the current page. Please contact jspenc35@utk.edu with this error and provide the report_id {report_id}.'
            raise Exception(err)
        return response.json()['results']
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
        self.users = self.get_report_results(args.user_report_id) 
        
        ### Pulling for /api/report/proposal_field here
        report_id_range = args.proposal_field_report_range.split(',')
        
        all_results = []
        for report_id in range(int(report_id_range[0].strip()), int(report_id_range[1].strip())+1):
            print(f'Pulling results for report id {report_id}.')
            results = self.get_report_results(report_id)
            all_results = [*all_results, *results]
        self.all_proposal_data = all_results
    # def get_report_state(self):
    #     """Queries the Curriculog API to return the state of a given report. Reports may be in a QUEUED, RUNNING, or ERROR state."""
    
    def write_json(self, data, file_name):
        """Write out an API response"""
        with open(f'{file_name}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
