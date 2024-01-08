from fpdf import FPDF
from fpdf.html import HTML2FPDF
import os
#Monkeypatch HTMLMixin
class HTMLMixin(object):
    def write_html(self, text, image_map=None):
        "Parse HTML and convert it to PDF"
        h2p = HTML2FPDF(self, image_map)
        #text = h2p.unescape(text) # To deal with HTML entities
        text = html.unescape(text)
        h2p.feed(text)
class MyFPDF(FPDF, HTMLMixin):
    pass

# pdf = MyFPDF()
# #First page
# pdf.add_page()
# pdf.write_html(html)
# pdf.output('html.pdf', 'F')
from html.parser import HTMLParser
import html
#h2p = HTML2FPDF(self, image_map)
class Doc:
    def __init__(self, college, college_type, program_type):
        """Constructor for a Showcase Doc for a given college. Showcase Docs have a page indicating the start of each data type, e.g., START 2023-2024 UG Add Program."""
        self.college = college
        self.college_type = college_type
        self.program_type = program_type
        self.output_file_path = ''
        self._get_output_file_path()
        self.pdf = MyFPDF()
        self.raw_data = ''
        self.data_types = set()
        # self.add_page_for_datatype(data_type)
        # self.write_html(proposal_showcase_html, proposal_link)
    def _get_output_file_path(self):
        """The college name is used in the filename for the output file. We need to standardize it so filenames follow a consistent format. Also filepaths are at max ~255 characters, so we have to account for this."""
        college = self.college.lower()
        college = college.split()
        college = "_".join(college)
        self.college = college
        self.output_file_path = f'{college}_{self.college_type}_{self.program_type}_showcases.pdf'
        #self.output_file_path = f'{os.getcwd()}/{self.college_type}_showcases/{college}_showcases.pdf'
        output_file_path_length = len(self.output_file_path)
        if output_file_path_length > 255:
            output_file_path_length_wo_college = output_file_path_length - len(college)
            max_length_college_name = 254 - output_file_path_length_wo_college
            college = college[0: max_length_college_name]
            self.output_file_path = f'{os.getcwd()}/showcases/{college}_showcases.pdf'
    def add_page_for_datatype(self, data_type):
        """Adds a title page to the growing PDF doc indicating the start of a new type of program proposal."""
        if data_type not in self.data_types:
            self.data_types.add(data_type)
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B",26)
            self.pdf.write(26, f'START {data_type}')
            self.pdf.add_page()
    def write_html(self, proposal_showcase_html, proposal_link):
        """Adds a page to self.pdf with the proposal showcase and a link to the proposal."""
        self.pdf.write(10, f'The following showcase corresponds to the proposal found at {proposal_link}\n')
        #print(proposal_showcase_html)
        self.pdf.write(16, proposal_showcase_html)
        #self.pdf.write_html(proposal_showcase_html)
        self.pdf.add_page()
    def save_pdf(self):
        """Writes self.pdf to pdf doc."""
        output_dir = f'showcases/{self.college_type}_showcases/{self.college}/'
        os.makedirs(output_dir, exist_ok=True)
        # print(f'Saving file to {self.output_file_path}')
        if len(self.raw_data) > 0:
            with open(f'{output_dir}{self.college}_{self.college_type}_{self.program_type}_showcases.html', 'w+', encoding='utf-8', errors='ignore') as html_file:
                html_file.write(self.raw_data)
                #print(f'Raw data {self.raw_data}')
                print(f' SUCCESSFULLY WROTE TO{output_dir}{self.college}_{self.college_type}_{self.program_type}_showcases.html')
        # self.pdf.output(self.output_file_path)