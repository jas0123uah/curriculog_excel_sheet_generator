import os

class Doc:
    def __init__(self, college, college_type, program_type):
        """Constructor for a Showcase Doc for a given college. Showcase Docs have a page indicating the start of each data type, e.g., START 2023-2024 UG Add Program."""
        self.college = college
        self.college_type = college_type
        self._program_type = program_type
        self.raw_data = ''
        self.proposals_in_department = ''
        self.data_types = set()
    @property
    def program_type(self):
        normalized_program_type = self._program_type.lower().replace(' ', '_')
        normalized_program_type = normalized_program_type.replace('/', '_')
        return normalized_program_type
    def save_concatenated_html(self):
        """Writes self.raw_data to an html file."""
        output_dir = f'showcases/{self.college_type}_showcases/{self.college}/'
        os.makedirs(output_dir, exist_ok=True)
        if len(self.raw_data) > 0:
            with open(f'{output_dir}{self.college}_{self.college_type}_{self.program_type}_showcases.html', 'w+', encoding='utf-8', errors='ignore') as html_file:
                html_file.write(self.raw_data)
                print(f' SUCCESSFULLY WROTE TO {output_dir}{self.college}_{self.college_type}_{self.program_type}_showcases.html')
    
    def save_proposals_in_department(self, department, action):
        """Writes self.proposals_in_department to an html file."""
        output_dir = f'showcases/{self.college_type}_showcases/{self.college}/{department}/{action}/'
        os.makedirs(output_dir, exist_ok=True)
        if len(self.proposals_in_department) > 0:
            output_file = f'{output_dir}{action}_ALL_showcases.html'
            if os.path.exists(output_file):
                os.remove(output_file)
            with open(output_file, 'w+', encoding='utf-8', errors='ignore') as html_file:
                html_file.write(self.proposals_in_department)
                print(f' SUCCESSFULLY WROTE TO {output_file}')
        self.proposals_in_department = ''

    def save_currrent_showcase(self, current_showcase_html, department, corresponding_dprog, action):
        """Writes the current showcase to an html file."""
        output_dir = f'showcases/{self.college_type}_showcases/{self.college}/{department}/{action}/{corresponding_dprog}/'
        print('MAKING DIR', output_dir)
        os.makedirs(output_dir, exist_ok=True)
        if len(current_showcase_html) > 0:
            output_file = f'{output_dir}{corresponding_dprog}_{self.program_type}_showcase.html'
            if os.path.exists(output_file):
                os.remove(output_file)
                output_file = f'{output_dir}{corresponding_dprog}_{self.program_type}_showcase.html'
            print('WRITING TO FILE', output_file)
            with open(output_file, 'w+', encoding='utf-8', errors='ignore') as html_file:
                html_file.write(current_showcase_html)
                print(f' SUCCESSFULLY WROTE TO {output_file}')
