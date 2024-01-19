import os

class Doc:
    def __init__(self, college, college_type, program_type):
        """Constructor for a Showcase Doc for a given college. Showcase Docs have a page indicating the start of each data type, e.g., START 2023-2024 UG Add Program."""
        self.college = college
        self.college_type = college_type
        self.program_type = program_type
        self.raw_data = ''
        self.data_types = set()
    def save_pdf(self):
        """Writes self.pdf to pdf doc."""
        output_dir = f'showcases/{self.college_type}_showcases/{self.college}/'
        os.makedirs(output_dir, exist_ok=True)
        if len(self.raw_data) > 0:
            with open(f'{output_dir}{self.college}_{self.college_type}_{self.program_type}_showcases.html', 'w+', encoding='utf-8', errors='ignore') as html_file:
                html_file.write(self.raw_data)
                print(f' SUCCESSFULLY WROTE TO {output_dir}{self.college}_{self.college_type}_{self.program_type}_showcases.html')
