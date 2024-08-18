import asyncio
from playwright.async_api import Playwright, async_playwright, expect, Browser, BrowserContext, Page
import pandas as pd
import xml.etree.ElementTree as ET
import re
import datetime
import requests
from requests_html import HTML
from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, send_file, make_response

class DOCTOR_DATA:
    def __init__(self):
        self.processes = 20
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
        self.page_2: Page = None
        self.cookies = {
    'ASP.NET_SessionId': '',
}
    async def progress_bar(self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
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
            
    async def get_current_date(self):
        self.max_auth_date = datetime.datetime.now()
        self.min_auth_date = self.max_auth_date - datetime.timedelta(days=90)
        self.min_auth_date = self.min_auth_date.strftime("%Y-%m-%d")
        self.max_auth_date = self.max_auth_date.strftime("%Y-%m-%d")
    
    async def run(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page1 = await self.context.new_page()
        self.page = await self.context.new_page()
        await self.page.goto("https://autregweb.sst.dk/authorizationsearch.aspx", wait_until='load', timeout=1000000)
        cookies = await self.page.context.cookies()
        for cookie in cookies:
            if cookie['name'] == 'ASP.NET_SessionId':
                self.cookies[cookie['name']] = cookie['value']
        
    async def enter_NameTextBox(self, name="Læge"):
        await self.page.wait_for_selector('[id="NameTextBox"]', state='visible', timeout=1000000)
        if name:
            self.name = name    
        await self.page.locator('[id="NameTextBox"]').fill(self.name)
    
    async def select_dropdown(self, name="Læge"):
        await self.page.wait_for_selector('[id="ProfessionTypeList"]', state='visible', timeout=1000000)
        await self.page.get_by_label("Faggruppe:").select_option(name)
        
    async def enter_Birthdate(self):
        await self.page.locator("#BirthdateMinDay").fill(self.min_birthdate.split("-")[2])
        await self.page.locator("#BirthdateMinMonth").fill(self.min_birthdate.split("-")[1])
        await self.page.locator("#BirthdateMinYear").fill(self.min_birthdate.split("-")[0])
        await self.page.locator("#BirthdateMaxDay").fill(self.max_birthdate.split("-")[2])
        await self.page.locator("#BirthdateMaxMonth").fill(self.max_birthdate.split("-")[1])
        await self.page.locator("#BirthdateMaxYear").fill(self.max_birthdate.split("-")[0])
    
    async def enter_AuthorizationId(self):
        await self.page.locator("#AuthIdTextBox").fill(self.authorization_id)
        
    async def enter_AuthorizationDate(self):
        await self.page.locator("#AuthDateMinDay").fill(self.min_auth_date.split("-")[2])
        await self.page.locator("#AuthDateMinMonth").fill(self.min_auth_date.split("-")[1])
        await self.page.locator("#AuthDateMinYear").fill(self.min_auth_date.split("-")[0])
        await self.page.locator("#AuthDateMaxDay").fill(self.max_auth_date.split("-")[2])
        await self.page.locator("#AuthDateMaxMonth").fill(self.max_auth_date.split("-")[1])
        await self.page.locator("#AuthDateMaxYear").fill(self.max_auth_date.split("-")[0])
    
    async def click_SearchButton(self):
        await self.page.wait_for_selector('[name="SearchButton"]', state='visible', timeout=1000000)
        await self.page.locator('[name="SearchButton"]').click()
     
    def get_row_details_request(self, link):
        cookies = {
    'ASP.NET_SessionId': self.cookies['ASP.NET_SessionId'],
}

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-GPC': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        while True:
            try:
                response = requests.get(link, headers=headers, cookies=cookies, timeout=1000000,stream=True)
                content = response.content
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        content += chunk
                html = HTML(html=content)
                tbody = html.find('[class="Practitioner"] tbody', first=True)
                row_details = {}
                try:
                    key = re.sub(r'[^\w]', '', tbody.find('#PersonAuthorizationstatusLabel', first=True).text)
                    value = tbody.find('#PersonAuthorizationstatus', first=True).text.strip()
                    row_details[key] = value
                except:
                    pass
                for row in tbody.find('tr')[2:]:
                    columns = row.find('td')
                    if len(columns) == 2:
                        key = re.sub(r'[^\w]', '', columns[0].find('span', first=True).text)
                        if columns[1].find('span', first=True):
                            value = columns[1].find('span', first=True).text.strip()
                        else:
                            value = "N/A"
                        row_details[key] = value
                break
            except Exception as e:
                pass
        return row_details
          
    async def get_row_details(self, link):
        await self.page1.goto(link, wait_until='load', timeout=1000000)
        await self.page1.wait_for_selector('[class="Practitioner"] tbody', state='visible', timeout=1000000)
        tbody_rows = await self.page1.locator('[class="Practitioner"] tbody').locator('tr').all()
        row_details = {}
        for row in tbody_rows:
            await self.page1.wait_for_selector('td', state='visible', timeout=1000000)
            columns = await row.locator('td').locator('span').all()
            if len(columns) == 2:
                key = await columns[0].inner_text()
                key = re.sub(r'[^\w]', '', key)
                value = await columns[1].inner_text()
                value = value.strip()
                row_details[key] = value
        
        return row_details
                
    async def get_table_data(self):
        final_data = []
        scraped_pages = set()
        previous_scraped_pages = set()
        completed = False
        phase = 1
        while not completed:
            await self.page.wait_for_selector('[id="Caption"]', state='visible', timeout=1000000)
            pager = await self.page.locator('[id="pager"] a').all()
            if not pager:
                pager = await self.page.locator('[id="pager"] span').all()
            index = 0
            for pg in pager:
                pg_text = await pg.inner_text()
                try:
                    pg_text = int(pg_text)
                except:
                    if index != 0:
                        await pg.click()
                        break
                    else:
                        continue
                    
                await self.page.wait_for_selector('[id*="AuthorizationSearchView_HyperLink1"]', state='visible', timeout=1000000)
                html = await self.page.content()
                parsed_html = HTML(html=html)
                table_rows = parsed_html.find('[id*="AuthorizationSearchView_HyperLink1"]')
                valid_links = []
                for row in table_rows:
                    href = row.attrs['href']
                    if href is None:
                        continue
                    link = "https://autregweb.sst.dk/"+ href
                    valid_links.append(link)
                with ThreadPool(processes=self.processes) as pool:
                    results = pool.map(self.get_row_details_request, valid_links)
                for row_details in results:
                    final_data.append(row_details)
                scraped_pages.add(pg_text)
                await self.progress_bar(index, len(pager), prefix = f'PHASE: {phase} PAGE: {pg_text} PROGRESS:', suffix = f'COMPLETEd {index+1}/{len(pager)}', length = 50)
                
                if len(previous_scraped_pages) == len(scraped_pages):
                    print("Completed", pg_text, len(scraped_pages)==len(previous_scraped_pages),not pg_text == "..." and isinstance(pg_text, int))
                    completed = True
                    break
                previous_scraped_pages = scraped_pages.copy()
                await pg.click()
                index += 1
            phase += 1   
        df = pd.DataFrame(final_data)
        df.to_xml("doctors_data.xml", root_name="Doctors", row_name="Doctor", index=False)
        df.to_excel("doctors_data.xlsx", index=False)
        
    async def close(self):
        try:
            await self.playwright.stop()
        except:
            pass
        
    async def main(self):
        await self.run()
        await self.select_dropdown()
        await self.get_current_date()
        await self.enter_AuthorizationDate()
        await self.click_SearchButton()
        await self.get_table_data()
        await self.close()
        
if __name__ == "__main__":
    doctor_data = DOCTOR_DATA()
    asyncio.run(doctor_data.main())
    