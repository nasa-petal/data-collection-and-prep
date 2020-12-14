from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome('/Users/jerryqian/Downloads/chromedriver', options=options)


df = pd.read_csv('cleaned_papers_for_labeling.csv')

def science_daily_scraper(row):
    url = row['Journal URL']
    press_release = row['Press release']
    if pd.isnull(url) and not pd.isnull(press_release) and 'sciencedaily' in press_release:
        driver.get(press_release)

        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'lxml')

        #If the "journal_references" section exists
        try:
            journal_div = soup.find('div', id='journal_references')
            url = journal_div.find('a')['href']
        #Return the same url if it doesn't exist
        except:
            pass
    return url

df['Journal URL'] = df.apply(science_daily_scraper, axis = 1)

df.to_csv('scraped_papers_for_labeling.csv')