from curriculog_excel_sheet_generator.classes.showcase_downloader import ShowcaseDownloader
from tkinter import messagebox
def download_showcases():
    downloader = ShowcaseDownloader()
    downloader.download_showcases()
    messagebox.showinfo('Curriculog Showcase Downloader', 'Showcase docs downloaded successfully!')