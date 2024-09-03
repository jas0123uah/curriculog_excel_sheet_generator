from curriculog_excel_sheet_generator.classes.report_generator import ReportGenerator
import dotenv, os
dotenv_file =dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
print('REFRESHING CURRICULOG API TOKEN')
report_creator = ReportGenerator(api_token= os.environ["API_KEY"])

new_api_token = report_creator.refresh_api_token()
os.environ["API_KEY"] = new_api_token

# Save the new API token to the.env file
dotenv.set_key(dotenv_file, "API_KEY", os.environ["API_KEY"])
print('REFRESHED CURRICULOG API TOKEN SUCCESSFULLY!')