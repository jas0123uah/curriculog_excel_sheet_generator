import requests
from pprint import pprint
class ReportGenerator:
    def __init__(self, api_token, report_id = None) -> None:
        self.api_token = api_token
        self.base_url = 'https://utk.curriculog.com'
        self.report_id = report_id
    def run_report(self, report_name):
        """Takes a given report name available within the Curriculog API and submits a request to run the report."""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        }
        if report_name == 'proposal_report':
            #api_endpoint = '/api/v1/report/proposal_field/'
            api_endpoint = '/api/v1/report/proposal/'



        
        url = f'{self.base_url}{api_endpoint}'
        first_go = True
        response = requests.post(url=url, headers=headers, allow_redirects=True)
        pprint(vars(response))
        # while first_go is True or getattr(response, 'status_code') =='404':

        #     pprint(vars(response))
        #     print(f'TRYING AGAIN WITH URL {response.url} \n\n\n')


        
    def get_report_state(self):
        """Queries the Curriculog API to return the state of a given report. Reports may be in a QUEUED, RUNNING, or ERROR state."""
    def get_report_results(self):
        """Stores and returns the results for a Curriculog API."""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        }
        api_endpoint = f'/api/v1/report/result/{self.report_id}'
        url = f'{self.base_url}{api_endpoint}'
        response = requests.get(url=url, headers=headers, allow_redirects=True)
        pprint(vars(response))
        # while self.report_state is None or self.report_state != ''
