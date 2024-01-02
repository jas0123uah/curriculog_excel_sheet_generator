class ShowcaseDownloader:
    def __init__(self, undergraduate_program_proposals, graduate_program_proposals):
        """Constructor for Showcase Downloader instance. The Showcase Downloader is meant to iterate over pandas dataframes of undergraduate and graduate program proposals and create concatenated HTML docs for each college."""
        self.undergraduate_program_proposals = undergraduate_program_proposals
        self.graduate_program_proposals = graduate_program_proposals
        #One DOC per college
        self.undergrad_docs = []
        self.grad_docs = []
    