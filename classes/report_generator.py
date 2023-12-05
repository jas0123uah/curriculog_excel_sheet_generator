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
    
    def get_proposal_list(self): 
        """Calls /api/v1/reports/proposal to return a list of all Curriculog proposals in the system. Also stores results on ReportGenerator instance under proposal_list."""
        api_endpoint = '/api/v1/report/proposal/'
        
        url = f'{self.base_url}{api_endpoint}'
        response = requests.post(url=url, headers=self.headers, allow_redirects=True)
        report_id = response.json()['report_id']
        #report_id = '838'
        proposal_list = self.get_report_results(report_id)
        self.proposal_list = proposal_list
        return proposal_list

    def get_ap_ids(self): 
        """Loops over proposal_list to return a unique list of ap_ids."""
        ap_ids = []
        for proposal in self.proposal_list:
            if proposal['ap_id'] not in ap_ids:
                ap_ids.append(proposal['ap_id'])
        self.ap_ids = ap_ids
        return ap_ids
    
    def get_all_proposal_fields(self, api_filters):
        """Loops over self.ap_ids calling _get_proposal_fields."""
        all_proposals_w_data = []
        print(self.ap_ids)
        for ap_id in self.ap_ids:
            print(f'Getting proposal fields for ap_id {ap_id}')
            proposals_w_data = self._get_proposal_fields(ap_id, api_filters=api_filters)
            all_proposals_w_data = [*all_proposals_w_data, *proposals_w_data]
        self.all_proposal_data = all_proposals_w_data
        self.write_json(all_proposals_w_data, 'proposals.json')
            

    def _get_proposal_fields(self, ap_id, api_filters = {}): 
        """Calls /api/v1/report/proposal_field/ with ap_id to return proposals matching a specific approval process id."""
    
        api_endpoint = '/api/v1/report/proposal_field/'
        url = f'{self.base_url}{api_endpoint}'
        
        print(f'API filters: {api_filters}')
        data = {"ap_id": ap_id }
        data.update(api_filters)
        data = json.dumps(data)
        response = requests.post(url=url, headers=self.headers, allow_redirects=True, data=data)
        print(response.json())
        report_id = response.json()['report_id']
        
        print(f'{report_id} will contain results for proposal fields with api_id {ap_id}.')
        return self.get_report_results(report_id)

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
    
        
    # def get_report_state(self):
    #     """Queries the Curriculog API to return the state of a given report. Reports may be in a QUEUED, RUNNING, or ERROR state."""
    
    def write_json(self, data, file_name):
        """Write out an API response"""
        with open(f'{file_name}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
