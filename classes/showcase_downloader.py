from .doc import Doc
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

#driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
class ShowcaseDownloader:
    def __init__(self, undergraduate_program_proposals, graduate_program_proposals, args):
        """Constructor for Showcase Downloader instance. The Showcase Downloader is meant to iterate over pandas dataframes of undergraduate and graduate program proposals and create concatenated HTML docs for each college."""
        self.undergraduate_program_proposals = undergraduate_program_proposals
        self.graduate_program_proposals = graduate_program_proposals
        service = webdriver.ChromeService()
        print('Using ChromeDriver')
        self.driver =webdriver.Chrome(service=service)
        print('EdgeDriver Loaded')
        self.args = args
        #self.driver = webdriver.Edge(EdgeChromiumDriverManager().install())
    def _open_login(self):
        """Clicks the login button to navigate to the login page.
        """   
        self.driver.get('https://utk.curriculog.com')  
        self.driver.maximize_window()
        time.sleep(5)  
        login_link = self.driver.find_element(By.ID, 'login')
        login_link.click()
    def _login(self):
        """Identifies the NetID and Password fields. Attempts to log the user in via passed in CLI args."""
        netid_field = self.driver.find_element(By.ID, 'username')
        password_field = self.driver.find_element(By.ID, 'password')
        netid_field.send_keys(self.args.netid)
        password_field.send_keys(self.args.password)
        password_field.send_keys(Keys.ENTER)
        self._send_duo_push()
    
    def _send_duo_push(self):
        """Clicks the button to send the logged in user a push notification to authorize login"""
        time.sleep(5)
        send_me_a_push_button = self.driver.find_element(By.CLASS_NAME, "auth-button")
        send_me_a_push_button.click()
        #Give plenty of time for the push notification to get to the user's phone.
        time.sleep(7)
    def download_showcases(self):
        """Iterates over the undergraduate and graduate program proposals and creates concatenated PDF for each college."""
        self._open_login()
        self._login()
        college_types = ['undergraduate', 'graduate']
        for college_type in college_types:
            #print(list(self.undergraduate_program_proposals.columns))
            if college_type == 'undergraduate':
                target_program_type = self.undergraduate_program_proposals
                #colleges_in_college_type = self.undergraduate_program_proposals['College'].unique()
            else:
                target_program_type = self.graduate_program_proposals
                #colleges_in_college_type = self.graduate_program_proposals['College'].unique()
            colleges_in_college_type = target_program_type['College'].unique()

        
            for college in colleges_in_college_type:
                print(f'This is the college: {college}')
                undergrad_showcases_in_college = Doc(college, college_type)
                #self.concatenated_dataframe = self.concatenated_dataframe[self.concatenated_dataframe[filter_item.field_name] == filter_item.values[0]]
                proposals_in_colllege = target_program_type[target_program_type['College'] == college] 
                program_proposal_types = target_program_type['Action'].unique()
                for program_type in program_proposal_types:
                    print(f'Getting {college_type} proposals in college {college} for program type {program_type}')
                    undergrad_showcases_in_college.add_page_for_datatype(program_type)
                    print(f'These are proposals in college {proposals_in_colllege}')

                    proposals_in_colllege = proposals_in_colllege[proposals_in_colllege['Action'] == program_type]
                    for idx, row in proposals_in_colllege.iterrows():
                        url = row['URL']
                        print(f'Getting showcase at url: {url}')
                        self.driver.get(url)
                        time.sleep(5)
                        showcase_html = self.open_showcase_window()
                        #time.sleep(20)
                        undergrad_showcases_in_college.write_html(showcase_html, url)
                        undergrad_showcases_in_college.raw_data += showcase_html
                        print("SUCCESSFULLY WROTE HTML")
                undergrad_showcases_in_college.save_pdf()
    def open_showcase_window(self):
        """Opens the showcase window from the current page. Returns the html of the showcase window."""
        try:
            preview_curriculum_button = self.driver.find_element(By.CLASS_NAME, 'preview-curriculum')
        except NoSuchElementException:
            return 'No preview found'
        # self.driver.execute_script("arguments[0].scrollIntoView();", preview_curriculum_button)
        # time.sleep(7)
        preview_curriculum_button.click()
        time.sleep(7)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        images = self.driver.find_elements(By.TAG_NAME, 'img')
        anchors = self.driver.find_elements(By.TAG_NAME, 'a')
        tables = self.driver.find_elements(By.TAG_NAME, 'table')
        for table in tables:
            self.driver.execute_script("arguments[0].setAttribute('width',arguments[1])",table, '100')
        els = [*anchors, *images]
        for image in els:
            self.driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, image)
            print('REMOVED IMAGE')

        html = self.driver.page_source
        
        #html = self.driver.find_element(By.TAG_NAME, 'html').text
        print(f'This is HTML: {html}')
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        return html


    