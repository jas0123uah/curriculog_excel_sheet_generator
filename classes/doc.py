#from fpdf import FPDF
#from fpdf.html import HTML2FPDF
import os
#Monkeypatch HTMLMixin
# class HTMLMixin(object):
#     def write_html(self, text, image_map=None):
#         "Parse HTML and convert it to PDF"
#         h2p = HTML2FPDF(self, image_map)
#         text = html.unescape(text)
#         h2p.feed(text)
# class MyFPDF(FPDF, HTMLMixin):
#     pass

#import html
class Doc:
    def __init__(self, college, college_type, program_type):
        """Constructor for a Showcase Doc for a given college. Showcase Docs have a page indicating the start of each data type, e.g., START 2023-2024 UG Add Program."""
        self.college = college
        self.college_type = college_type
        self.program_type = program_type
        #self.pdf = MyFPDF()
        self.raw_data = ''
        self.data_types = set()

    # def write_html(self, proposal_showcase_html, proposal_link):
    #     """Adds a page to self.pdf with the proposal showcase and a link to the proposal."""
    #     self.pdf.write(10, f'The following showcase corresponds to the proposal found at {proposal_link}\n')
    #     self.pdf.write(16, proposal_showcase_html)
    #     self.pdf.add_page()
    def save_pdf(self):
        """Writes self.pdf to pdf doc."""
        output_dir = f'showcases/{self.college_type}_showcases/{self.college}/'
        os.makedirs(output_dir, exist_ok=True)
        if len(self.raw_data) > 0:
            with open(f'{output_dir}{self.college}_{self.college_type}_{self.program_type}_showcases.html', 'w+', encoding='utf-8', errors='ignore') as html_file:
                html_file.write(self.raw_data)
                print(f' SUCCESSFULLY WROTE TO {output_dir}{self.college}_{self.college_type}_{self.program_type}_showcases.html')
