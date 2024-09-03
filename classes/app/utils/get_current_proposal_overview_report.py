import os
from decouple import config
def get_current_proposal_overview_report():
    """Returns the path to the current proposal overview report if it exists. Otherwise returns None."""
    # if config('TOP_OUTPUT_DIR') does not exist, create it:
    if not os.path.exists(config('TOP_OUTPUT_DIR')):
        os.makedirs(config('TOP_OUTPUT_DIR'))
    proposal_overview_dir = os.path.join(config('TOP_OUTPUT_DIR'), 'proposal_overview', 'current')
    # Get the xlsx files in proposal_overview_dir
    excel_files = [os.path.join(proposal_overview_dir, f) for f in os.listdir(proposal_overview_dir) if f.endswith('.xlsx')]
    if len(excel_files) > 0:
        # Return the absolute path of the first xlsx file
        return os.path.abspath(excel_files[0])