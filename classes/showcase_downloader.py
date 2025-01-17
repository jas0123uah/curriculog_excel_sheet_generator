from .doc import Doc
import time, os
import pandas as pd
from .app.utils.get_current_proposal_overview_report import get_current_proposal_overview_report
from decouple import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures

truncated_department_names = {
    "CECS": "CECS",
    "School of Journalism and Media": "JMED",
    "Ecology and Evolutionary Biology": "EEB",
    "Theory and Practice in Teacher Education": "TPTE",
    "Earth, Environmental, and Planetary Sciences": "EEPS",
    "Political Science": "POLS",
    "Kinesiology, Recreation, and Sport Studies": "KNS",
    "Anthropology": "ANTH",
    "Chemistry": "CHEM",
    "Interdisciplinary Programs": "INPG",
    "Nutrition": "NUTR",
    "Counseling, Human Development, and Family Science": "CHDFS",
    "World Languages and Cultures": "WLC",
    "School of Art": "ART",
    "Sociology": "SOCI",
    "Classics": "CLAS",
    "Psychology": "PSYC",
    "Tombras School of Advertising and Public Relations": "ADPR",
    "School of Information Sciences": "INSC",
    "Retail, Hospitality, and Tourism Management": "RHTM",
    "University Honors": "UHON",
    "School of Communication Studies": "SCOM",
    "VetMed": "VET",
    "Applied Engineering and Technology": "APENGR",
    "Religious Studies": "REST",
    "English": "ENGL",
    "History": "HIST",
    "Philosophy": "PHIL",
    "Educational Leadership and Policy Studies": "EDUCPOL",
    "Geography and Sustainability": "GEOG",
    "Mathematics": "MATH",
    "Biomedical Engineering": "BME",
    "Chemical and Biomolecular Engineering": "CHEM-E",
    "Materials Science and Engineering": "MSE",
    "Electrical Engineering and Computer Science": "EECS",
    "HBS": "HBS",
    "Physics and Astronomy": "PHYS",
    "Division of Biology": "BIOL",
    "Theatre": "THEAT",
    "Engineering Fundamentals Program": "EF",
    "Nuclear Engineering": "NE",
    "Pre-Professional Programs": "PPP",
    "School of Interior Architecture": "IAR",
    "Mechanical, Aerospace, and Biomedical Engineering": "MECH_AERO_ENGR",
    "School of Design": "DSGN",
}
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
        self.webdrivers = []
        print('Trying to initiate showcase downloader')
        for _ in range(self.num_webdrivers):
            print('Trying to initiate service and options')
            service = webdriver.ChromeService()
            options = webdriver.ChromeOptions()
            options.add_argument('--headless=new')
            print('Initiated service and options')
            driver = webdriver.Chrome(service=service, options=options)
            print('Appending driver')
            self.webdrivers.append(driver)
        print('Loaded webdrivers')
        with open(os.path.join(config('MAIN_CURRICULOG_DIR'), f'showcase_css.css'), 'r', encoding='utf-8') as  css_file:
            css = css_file.read()
            self.css = css
        print('Initialized ShowcaseDownloader')
    def _get_proposal_list_report(self):
        """Returns a pandas dataframe of the proposal list report. If no such report exists an error is thrown."""
        dprog_overview_report =get_current_proposal_overview_report()

        if dprog_overview_report is None:
            raise Exception(f"There is no current Dprog Overview report. Please generate a {config('CATALOG_YEAR_DPROG_CHANGES_REPORT_NAME')} report and try downloading showcases again.")
        else:
            
            return pd.read_excel(dprog_overview_report)

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
            trust_browser_button = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, "trust-browser-button")))
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
            print(f'Logging in to driver {i}')
            self._open_login(driver)
            login_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "login")))
            login_button.click()
            #Convert to webdriver wait
            if config('NET_ID') == '' or config('PASSWORD') == '':
                raise ValueError('Config must have NetID and Password entered to download showcases!')
            netid_field = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, 'username')))
            password_field = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, 'password')))
            password_field = driver.find_element(By.ID, 'password')
            print(config('NET_ID'))
            print(config('PASSWORD'))
            netid_field.send_keys(config('NET_ID'))
            password_field.send_keys(config('PASSWORD'))
            password_field.send_keys(Keys.ENTER)
            print(f'ENTERED NETID AND PASSWORD FOR DRIVER {i}')
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
        print('Calling download_showcases')
        self._login()
        college_types = ['undergraduate']
        for college_type in college_types:
            if college_type == 'undergraduate':
                target_program_type = self.undergraduate_program_proposals
            else:
                target_program_type = self.graduate_program_proposals
            colleges_in_college_type = target_program_type['College'].unique()
            print(colleges_in_college_type)
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
                                department = truncated_department_names.get(department, department)
                                action = row['Action']
                                driver = self.webdrivers[idx % len(self.webdrivers)]
                                futures.append(executor.submit(self.download_showcase, url, undergrad_showcases_in_college, driver, department, action))
                            for future in concurrent.futures.as_completed(futures):
                                future.result()
                        normalized_program_type = program_type.lower().replace(' ', '_')
                        normalized_program_type = normalized_program_type.replace('/', '_')
                        undergrad_showcases_in_college.save_proposals_in_department(department=department, action=normalized_program_type)
                    undergrad_showcases_in_college.save_concatenated_html()

    def get_corresponding_dprog(self, proposal_url):
        """Returns the corresponding dprog for the given proposal url."""
        #return current millisecond
        # # Get the row in self.dprog_overview_table that matches the proposal url at 'Curriculog Link'
        df = self.proposal_list_report[self.proposal_list_report['URL'] == proposal_url]

        dprog = (
            df.iloc[0]["Dprog"]
            if pd.notna(df.iloc[0]["Dprog"]) 
            else str(int(round(time.time() * 1000)))
        ) 
        return dprog
    def download_showcase(self, url, undergrad_showcases_in_college, driver, department, action):
        """Take a driver thread and downloads the showcase."""
        try:
            print(f'Getting showcase at url: {url}')
            driver.get(url)
            time.sleep(4)
            showcase_html = self.open_showcase_window(driver)
            undergrad_showcases_in_college.raw_data+=showcase_html
            undergrad_showcases_in_college.proposals_in_department += showcase_html
            normalized_program_type = action.lower().replace(' ', '_')
            normalized_program_type = normalized_program_type.replace('/', '_')
            undergrad_showcases_in_college.save_currrent_showcase(current_showcase_html=showcase_html, corresponding_dprog=self.get_corresponding_dprog(proposal_url=url), department=department, action= normalized_program_type)
        except Exception as e:
            print(f'Error downloading showcase: {e}')
        