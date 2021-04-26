from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import re

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
path_to_driver = '/Users/jerryqian/Downloads/chromedriver'
driver = webdriver.Chrome(path_to_driver, options=options)

filename = 'Colleen and Alex-Grid view.csv'
df = pd.read_csv(filename)

def doi_scraper(row):
    url = row['Primary lit site']
    doi = row['DOI']
    print('url: ', url)
    if pd.notnull(url):
        driver.get(url)

        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'lxml')

        doi = ''

        #Pulling first DOI from href
        try:
            for a in soup.find_all('a', href=True):
                link = a['href']
                if 'doi.org' in link:
                    doi = link.split('doi.org/')[1]
                    break

            #Pulling first DOI from text
            #Example: https://jeb.biologists.org/content/223/20/jeb226654
            #DOI not embedded in a href, but can only be pulled by searching the text
            if len(doi) == 0:
                doi = soup(text=re.compile(r'doi'))[0].strip()
                #removing all characters before first number in DOI
                doi = re.search('[0-9].*', doi)[0]

            print('doi: ', doi)
            print('----------------------------------')
        except:
            return doi
    
    return doi

df['DOI'] = df.apply(doi_scraper, axis = 1)
df.to_csv('colleen_alex_scraped.csv')