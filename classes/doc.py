class Doc:
    def __init__(self, data, data_type, college):
        """Constructor for a Showcase Doc for a given college. Showcase Docs have a page indicating the start of each data type, e.g., START 2023-2024 UG Add Program."""
        self.college = college
        self.data_types = set()
        self.add_page_for_datatype(data_type)
        self.data_types = self.data_types.add(data_type)
    def add_page_for_datatype(self, data_type):
        """Adds a title page to the growing PDF doc indicating the start of a new type of program proposal."""
        if data_type not in self.data_types:
            self.data_types.add(data_type)