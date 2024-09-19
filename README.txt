First time setup Powerpoint here: https://liveutk-my.sharepoint.com/:p:/g/personal/jspenc35_vols_utk_edu/EZFQBKAw_g1CqLBq0f4EaoMBDB-sIC92ccJMD_y_P0F5WQ?e=O1tSp8&wdOrigin=TEAMS-MAGLEV.undefined_ns.rwc&wdExp=TEAMS-TREATMENT&wdhostclicktime=1726756283413&web=1

1. Open your computer's start menu
2. Search for and open Microsoft Store.
3. Search for and install Python 3.11 from the Microsoft Store
4. Determine which version of Windows you are on by opening the start menu and navigating to Settings --> About --> System Type
5. Download the version of Git (https://git-scm.com/download/win) corresponding to your version of Windows (​If your Windows is 64-bit, select the 64-bit Git. If your Windows is 32-bit, select the 32-bit Git.)
6. Navigate to your Downloads folder and double click the installer to enter your Netid and password to install Git.​ Click next through all of the setup wizard prompts. Finally, click Finish.​
7. Open your computer's start menu
8. Search for and open Terminal
9. Paste the following into the terminal and hit enter: git clone https://github.com/jas0123uah/curriculog_excel_sheet_generator.git
10.Paste the following into the terminal and hit enter: cd curriculog_excel_sheet_generator
11.Paste the following into the terminal and hit enter: pip install -r requirements.txt
12.Paste the following into the terminal and hit enter: python setup.py


After you have set the script up/ Regular use instructions:
1. Open your computer's start menu
2. Paste the following into the terminal and hit enter: cd curriculog_excel_sheet_generator
3. Paste the following into the terminal and hit enter: git pull
4. Log in to https://utk.curriculog.com/
5. Go under your name in the banner at the top of the site & click "My Settings"
6. Click your name.
7. Scroll down to the API Key Manager.
8. Under "Existing Keys", click the key icon to generate a fresh API key.
9. Copy the key.
10. Enter the following into the terminal: notepad .env
11. Delete everything after the = sign for API_KEY
12. After API_KEY= type '
13. Paste the copied API key
14. Type another ' to fully enclose the API key in single quotes. Ensure you don't have trailing spaces at the end of the API key you pasted.
15. Save the .env file.
16. Paste the following into the terminal and hit enter: python curriculog_report_generator.py
17. Click the "New Report Button" in the GUI.
18. Click the name of the report you are trying to generate.
19. Click Submit.
20. Watch the terminal for any errors. If errors occur, contact Jonathan Hughes or Jay Spencer
21. After the script runs successfully, close the GUI.
22. Paste the following into the terminal and hit enter: explorer.exe .
23. Navigate to output and open the folder with the name of the report you were trying to generate.
24. Go to the folder current. The excel document in this folder corresponds to the report you just ran.
25. Previous reports you ran will be under the folder previous.
26. Close the terminal.  
