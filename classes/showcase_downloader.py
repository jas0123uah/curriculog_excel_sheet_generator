from .doc import Doc
import time, os
import pandas as pd
from decouple import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures

class element_does_not_have_css_class(object):
  """An expectation for checking that an element has a particular css class.

  locator - used to find the element
  returns the WebElement once it has the particular css class
  """
  def __init__(self, locator, css_class):
    self.locator = locator
    self.css_class = css_class

  def __call__(self, driver):
    element = driver.find_element(*self.locator)   # Finding the referenced element
    if self.css_class not in element.get_attribute("class"):
        return element
    else:
        return False

class ShowcaseDownloader:
    def __init__(self):
        """Constructor for Showcase Downloader instance. The Showcase Downloader is meant to iterate over pandas dataframes of undergraduate and graduate program proposals and create concatenated HTML docs for each college."""
        #Load excel file in pandas dataframe

        self.proposal_list_report = self._get_proposal_list_report()
        programs = self.get_programs()
        self.undergraduate_program_proposals = programs["undergraduate_programs"]
        self.graduate_program_proposals = programs["graduate_programs"]
        self.num_webdrivers = int(config('NUM_WEBDRIVERS'))
        self.dprog_overview_table = pd.read_excel(config('DPROG_OVERVIEW_TABLE'))
        self.webdrivers = []
        for _ in range(self.num_webdrivers):
            service = webdriver.ChromeService()
            options = webdriver.ChromeOptions()
            options.add_argument('--headless=new')
            driver = webdriver.Chrome(service=service, options=options)
            self.webdrivers.append(driver)
        with open(os.path.join(config('MAIN_CURRICULOG_DIR'), f'showcase_css.css'), 'r', encoding='utf-8') as  css_file:
            css = css_file.read()
            self.css = css
    def _get_proposal_list_report(self):
        """Returns a pandas dataframe of the proposal list report. If no such report exists an error is thrown."""
        plr_dir = os.path.join(config('TOP_OUTPUT_DIR'), 'proposal_overview', 'current')
        # Get the xlsx files in plr_dir
        excel_files = [os.path.join(plr_dir, f) for f in os.listdir(plr_dir) if f.endswith('.xlsx')]

        if len(excel_files) == 0:
            raise Exception(f"{plr_dir} does not contain any xlsx files. Please generate a new report.")
        else:
            plr = excel_files[0]
            return pd.read_excel(plr)

    def get_programs(self):
        """Filter concatenated_proposals to identify only those that are for a Graduate or Undergraduate program. Stores programs under graduate_programs and undergraduate_programs, respectively."""
        # undergraduate_programs = self.proposal_list_report[(self.proposal_list_report['GR/UG'] == 'UG') &  (self.proposal_list_report['Proposal Type'] == 'program') &  (self.proposal_list_report['completed_date'].notnull())]
        undergraduate_programs = self.proposal_list_report[(self.proposal_list_report['GR/UG'] == 'UG') &  (self.proposal_list_report['Proposal Type'] == 'program') ]
        graduate_programs = self.proposal_list_report[(self.proposal_list_report['GR/UG'] == 'GR') &  (self.proposal_list_report['Proposal Type'] == 'program')]
        print(undergraduate_programs['URL'])
        return {'undergraduate_programs': undergraduate_programs, 'graduate_programs': graduate_programs}
    
    def _send_duo_push(self, driver):
        """Clicks the button to send the logged in user a push notification to authorize login"""
        try:
            print('SENDING DUO PUSH')
            trust_browser_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "trust-browser-button")))
            trust_browser_button.click()
        except TimeoutException:
            pass
        time.sleep(7)

    def _open_login(self, driver):
        """Opens the login page for each driver."""
        print('OPENING LOGIN PAGE')
        driver.get('https://utk.curriculog.com')
        driver.maximize_window()

    def _login(self):
        """Logs in to each driver."""
        for i, driver in enumerate(self.webdrivers):
            self._open_login(driver)
            login_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "login")))
            login_button.click()
            netid_field = driver.find_element(By.ID, 'username')
            password_field = driver.find_element(By.ID, 'password')
            netid_field.send_keys(config('NET_ID'))
            password_field.send_keys(config('PASSWORD'))
            password_field.send_keys(Keys.ENTER)
            self._send_duo_push(driver)
    
    def open_showcase_window(self, driver):
        """Opens the showcase window from the current page. Returns the html of the showcase window."""
        proposal_url = driver.current_url
        try:
            preview_curriculum_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'preview-curriculum')))
        except NoSuchElementException:
            print(f'No preview found for proposal found at {proposal_url}')
            return f'No preview found for proposal found at {proposal_url}'
        preview_curriculum_button.click()
        print(f'There are {len(driver.window_handles)} windows in the webdriver')

        driver.switch_to.window(driver.window_handles[-1])
        # Wait for the masked class to be removed from the body
        wait = WebDriverWait(driver, 10)
        wait.until(element_does_not_have_css_class((By.TAG_NAME, 'body'), "masked"))
        driver.find_element(By.CSS_SELECTOR, 'button#markup').click()
        wait.until(element_does_not_have_css_class((By.TAG_NAME, 'body'), "masked"))
        
        buttons = []
    
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        tables = driver.find_elements(By.TAG_NAME, 'table')

        for table in tables:
            driver.execute_script("arguments[0].setAttribute('width',arguments[1])",table, '100')
        els = [*buttons]
      
        for image in els:

            driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, image)



        head = driver.find_element(By.TAG_NAME, 'head')
        add_css_script = """
            var node = document.createElement("style");
            node.type = "text/css";
            node.appendChild(document.createTextNode(arguments[0]))        
            arguments[1].appendChild(node);
            """
        driver.execute_script(add_css_script, self.css, head)
        add_proposal_url_to_body_script = """
            var h1 = document.createElement("h1");
            h1.innerHTML = `The proposal below may be viewed <a href=${arguments[0]}>here</a>.`;
            arguments[1].prepend(h1);
            """
        body = driver.find_element(By.TAG_NAME, 'body')
        driver.execute_script(add_proposal_url_to_body_script, proposal_url, body)

        html = driver.page_source
        
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return html

    def download_showcases(self):
        """Iterates over the undergraduate and graduate program proposals and creates concatenated PDF for each college."""
        self._login()
        college_types = ['undergraduate']
        for college_type in college_types:
            if college_type == 'undergraduate':
                target_program_type = self.undergraduate_program_proposals
            else:
                target_program_type = self.graduate_program_proposals
            colleges_in_college_type = target_program_type['College'].unique()
            for college in colleges_in_college_type:
                proposals_in_college = target_program_type[target_program_type['College'] == college]
                program_proposal_types = proposals_in_college['Action'].unique()
                for program_type in program_proposal_types:
                    undergrad_showcases_in_college = Doc(college, college_type, program_type)
                    print(f'Getting {college_type} proposals in college {college} for program type {program_type}')
                    proposals_of_given_type_in_college = proposals_in_college[proposals_in_college['Action'] == program_type]
                    #proposals_of_given_type_in_college = proposals_of_given_type_in_college.head(3)

                    departments = proposals_of_given_type_in_college['Department'].unique()
                    for department in departments:
                        print(f'Getting {college_type} proposals in college {college} for program type {program_type} in department {department}')
                        proposals_of_given_type_in_department = proposals_of_given_type_in_college[proposals_of_given_type_in_college['Department'] == department]
                        #for idx, row in proposals_of_given_type_in_college.iterrows():
                            
                        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.webdrivers)) as executor:
                            futures = []
                            for idx, row in proposals_of_given_type_in_department.iterrows():
                                url = row['URL']
                                # print(f'THERES A PROPOSAL AT URL: {url}')
                                department = row['Department']
                                action = row['Action']
                                driver = self.webdrivers[idx % len(self.webdrivers)]
                                futures.append(executor.submit(self.download_showcase, url, undergrad_showcases_in_college, driver, department, action))
                            for future in concurrent.futures.as_completed(futures):
                                future.result()
                        undergrad_showcases_in_college.save_proposals_in_department(department=department, action=program_type)
                    undergrad_showcases_in_college.save_concatenated_html()

    def get_corresponding_dprog(self, proposal_url):
        """Returns the corresponding dprog for the given proposal url."""
        #return current millisecond
        # Get the row in self.dprog_overview_table that matches the proposal url at 'Curriculog Link'
        df = self.dprog_overview_table[self.dprog_overview_table['Curriculog Link'] == proposal_url]
        if df.empty:
            # We dont have a dprog for this proposal, just return the current millisecond
            return int(round(time.time() * 1000))
        dprog = df.iloc[0]['Dprog']
        return dprog.replace('/', '_')
    def download_showcase(self, url, undergrad_showcases_in_college, driver, department, action):
        """Take a driver thread and downloads the showcase."""
        try:
            print(f'Getting showcase at url: {url}')
            driver.get(url)
            time.sleep(4)
            showcase_html = self.open_showcase_window(driver)
            undergrad_showcases_in_college.raw_data+=showcase_html
            undergrad_showcases_in_college.proposals_in_department += showcase_html
            undergrad_showcases_in_college.save_currrent_showcase(current_showcase_html=showcase_html, corresponding_dprog=self.get_corresponding_dprog(proposal_url=url), department=department, action= action)
        except Exception as e:
            print(f'Error downloading showcase: {e}')
        