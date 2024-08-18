import os
import time
from playwright.sync_api import Playwright, sync_playwright, expect, Browser, BrowserContext, Page
import pandas as pd
import xml.etree.ElementTree as ET
import re
import datetime
from flask import Flask, send_file, make_response

class DOCTOR_DATA:
    def __init__(self):
        self.name = "Læge"
        self.min_birthdate = None
        self.max_birthdate = None
        self.authorization_id = None
        self.min_auth_date = None
        self.max_auth_date = None
        self.playwright: Playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.playwright_2: Playwright = None
        self.browser_2: Browser = None
        self.context_2: BrowserContext = None
        self.page_2: Page = None
    
    def progress_bar(self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
        """
        This function is used to display the progress bar

        Args:
            iteration (int): iteration number
            total (int): total number
            prefix (str): prefix string
            suffix (str): suffix string
            decimals (int): number of decimals
            length (int): length of the progress bar
            fill (str): fill character
            printEnd (str): print end character

        Returns:
            None
        """
        #make fill green
        fill = f'\033[92m{fill}\033[0m'
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
        if iteration == total: 
            print(flush=True)
            
    def get_current_date(self):
        self.max_auth_date = datetime.datetime.now()
        self.min_auth_date = self.max_auth_date - datetime.timedelta(days=90)
        self.min_auth_date = self.min_auth_date.strftime("%Y-%m-%d")
        self.max_auth_date = self.max_auth_date.strftime("%Y-%m-%d")
    
    def run(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page1 = self.context.new_page()
        self.page = self.context.new_page()
        self.page.goto("https://autregweb.sst.dk/authorizationsearch.aspx", wait_until='load', timeout=1000000)
        
        
    def enter_NameTextBox(self, name="Læge"):
        self.page.wait_for_selector('[id="NameTextBox"]', state='visible', timeout=1000000)
        if name:
            self.name = name    
        self.page.locator('[id="NameTextBox"]').fill(self.name)
    
    def select_dropdown(self, name="Læge"):
        self.page.wait_for_selector('[id="ProfessionTypeList"]', state='visible', timeout=1000000)
        self.page.get_by_label("Faggruppe:").select_option(name)
        
    def enter_Birthdate(self):
        self.page.locator("#BirthdateMinDay").fill(self.min_birthdate.split("-")[2])
        self.page.locator("#BirthdateMinMonth").fill(self.min_birthdate.split("-")[1])
        self.page.locator("#BirthdateMinYear").fill(self.min_birthdate.split("-")[0])
        self.page.locator("#BirthdateMaxDay").fill(self.max_birthdate.split("-")[2])
        self.page.locator("#BirthdateMaxMonth").fill(self.max_birthdate.split("-")[1])
        self.page.locator("#BirthdateMaxYear").fill(self.max_birthdate.split("-")[0])
    
    def enter_AuthorizationId(self):
        self.page.locator("#AuthIdTextBox").fill(self.authorization_id)
        
    def enter_AuthorizationDate(self):
        self.page.locator("#AuthDateMinDay").fill(self.min_auth_date.split("-")[2])
        self.page.locator("#AuthDateMinMonth").fill(self.min_auth_date.split("-")[1])
        self.page.locator("#AuthDateMinYear").fill(self.min_auth_date.split("-")[0])
        self.page.locator("#AuthDateMaxDay").fill(self.max_auth_date.split("-")[2])
        self.page.locator("#AuthDateMaxMonth").fill(self.max_auth_date.split("-")[1])
        self.page.locator("#AuthDateMaxYear").fill(self.max_auth_date.split("-")[0])
    
    def click_SearchButton(self):
        self.page.wait_for_selector('[name="SearchButton"]', state='visible', timeout=1000000)
        self.page.locator('[name="SearchButton"]').click()
       
    def get_row_details(self, link):
        self.page1.goto(link, wait_until='load', timeout=1000000)
        self.page1.wait_for_selector('[class="Practitioner"] tbody', state='visible', timeout=1000000)
        tbody_rows = self.page1.locator('[class="Practitioner"] tbody').locator('tr').all()
        row_details = {}
        for row in tbody_rows:
            self.page1.wait_for_selector('td', state='visible', timeout=1000000)
            columns = row.locator('td').locator('span').all()
            if len(columns) == 2:
                key = re.sub(r'[^\w]', '', columns[0].inner_text())
                value = columns[1].inner_text().strip()
                row_details[key] = value
        
        return row_details
                
    def get_table_data(self):
        
        final_data = []
        final_xml = []
        scraped_pages = set()
        previous_scraped_pages = set()
        completed = False
        while not completed:
            self.page.wait_for_selector('[id="Caption"]', state='visible', timeout=1000000)
            pager = self.page.locator('[id="pager"] a').all()
            if not pager:
                pager = self.page.locator('[id="pager"] span').all()
            for pg in pager:
                self.page.wait_for_selector('[id*="AuthorizationSearchView_HyperLink1"]', state='visible', timeout=1000000)
                table_rows = self.page.locator('[id*="AuthorizationSearchView_HyperLink1"]').all()
                for row in table_rows:
                    self.page.wait_for_selector('[id*="AuthorizationSearchView_HyperLink1"]', state='visible', timeout=1000000)
                    href = row.get_attribute('href')
                    if href is None:
                        continue
                    link = "https://autregweb.sst.dk/"+ href
                    
                    row_details = self.get_row_details(link)
            
                    final_data.append(row_details)
                scraped_pages.add(pg.inner_text())        
                if len(previous_scraped_pages) == len(scraped_pages):
                    print("Completed", pg.inner_text(), len(scraped_pages)==len(previous_scraped_pages),not pg.inner_text() == "..." and isinstance(pg.inner_text(), int))
                    completed = True
                    break
                pg.click()
                previous_scraped_pages = scraped_pages.copy()
                
        df = pd.DataFrame(final_data)
        df.to_xml("doctors_data.xml", root_name="Doctors", row_name="Doctor", index=False)
    
    def close(self):
        self.context.close()
        self.browser.close()
    def main(self):
        self.run()
        self.select_dropdown("Læge")
        self.get_current_date()
        self.enter_AuthorizationDate()
        self.click_SearchButton()
        self.get_table_data()
        self.close()
    
app = Flask(__name__)

@app.route('/get-xml', methods=['GET'])
def get_xml():
    # Create a sample DataFrame
    current_dir = os.path.dirname(__file__)
    file_name = os.path.join(current_dir, 'doctors_data.xml')
    df = pd.read_xml(file_name)
    # Convert the DataFrame to XML
    xml = df.to_xml()
    # Create a response
    response = make_response(xml)
    response.headers['Content-Type'] = 'application/xml'
    response.headers['Content-Disposition'] = 'attachment; filename=doctors_data.xml'
    return response

    
if __name__ == '__main__':
    doctor_data = DOCTOR_DATA()
    doctor_data.main()
    app.run(debug=True)