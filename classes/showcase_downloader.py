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
        self.driver =webdriver.Chrome(service=service)
        self.args = args
        with open(f'showcase_css.css', 'r', encoding='utf-8') as  css_file:
            css = css_file.read()
            self.css = css
           
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
        college_types = ['undergraduate']
        for college_type in college_types:
            if college_type == 'undergraduate':
                target_program_type = self.undergraduate_program_proposals
            else:
                target_program_type = self.graduate_program_proposals
            colleges_in_college_type = target_program_type['College'].unique()
            colleges_in_college_type = ['TCE', 'University Exploratory' ,'University Honors',
 'University Transition']
         
            print(f'These are the colleges {colleges_in_college_type}')


        
            for college in colleges_in_college_type:
                college = 'No College' if college == '' else college 

                proposals_in_college = target_program_type[target_program_type['College'] == college] 
                program_proposal_types = proposals_in_college['Action'].unique()
                for program_type in program_proposal_types:
                    undergrad_showcases_in_college = Doc(college, college_type, program_type)
                    print(f'Getting {college_type} proposals in college {college} for program type {program_type}')

                    proposals_of_given_type_in_college = proposals_in_college[proposals_in_college['Action'] == program_type]
                    for idx, row in proposals_of_given_type_in_college.iterrows():
                        url = row['URL']
                        print(f'Getting showcase at url: {url}')
                        self.driver.get(url)
                        time.sleep(4)
                        #time.sleep(10)
                        showcase_html = self.open_showcase_window()
                        undergrad_showcases_in_college.raw_data += showcase_html
                    undergrad_showcases_in_college.save_pdf()
    def open_showcase_window(self):
        """Opens the showcase window from the current page. Returns the html of the showcase window."""
        proposal_url = self.driver.current_url
        try:
            preview_curriculum_button = self.driver.find_element(By.CLASS_NAME, 'preview-curriculum')
        except NoSuchElementException:
            print(f'No preview found for proposal found at {proposal_url}')
            return f'No preview found for proposal found at {proposal_url}'

        preview_curriculum_button.click()
        #time.sleep(7)
        time.sleep(2)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.find_element(By.CSS_SELECTOR, 'button#markup').click()
        time.sleep(6)
        images = self.driver.find_elements(By.TAG_NAME, 'img')
        buttons = []
        buttons = self.driver.find_elements(By.TAG_NAME, 'button')
        tables = self.driver.find_elements(By.TAG_NAME, 'table')
        for table in tables:
            self.driver.execute_script("arguments[0].setAttribute('width',arguments[1])",table, '100')
        els = [*buttons]
        for image in els:
            self.driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, image)
        head = self.driver.find_element(By.TAG_NAME, 'head')
        add_css_script = """
            var node = document.createElement("style");
            node.type = "text/css";
            node.appendChild(document.createTextNode(arguments[0]))        
            arguments[1].appendChild(node);
            """
        self.driver.execute_script(add_css_script, self.css, head)
        add_proposal_url_to_body_script = """
            var h1 = document.createElement("h1");
            h1.innerHTML = `The proposal below may be viewed <a href=${arguments[0]}>here</a>.`;
            arguments[1].prepend(h1);
            """
        body = self.driver.find_element(By.TAG_NAME, 'body')
        self.driver.execute_script(add_proposal_url_to_body_script, proposal_url, body)

        html = self.driver.page_source
        
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        return html


    