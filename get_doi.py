#A script that pulls DOI from any journal publication website
import requests
from bs4 import BeautifulSoup
import re
import argparse
import sys

def pull_doi(url):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    doi = ''

    #Pulling first DOI from href
    for a in soup.find_all('a', href=True):
        link = a['href']
        if 'doi.org' in link:
            doi = link.split('doi.org/')[1]
            break

    #Pulling first DOI from text
    #Example: https://jeb.biologists.org/content/223/20/jeb226654
    #DOI not embedded in a href, but can only be pulled by searching the text
    if len(doi) == 0:
        print('pulling from text')
        doi = soup(text=re.compile(r'doi'))[0].strip()
        #removing all characters before first number in DOI
        doi = re.search('[0-9].*', doi)[0]

    return doi

if __name__ == "main":
    parser = argparse.ArgumentParser(description='Pull DOI from Any Journal Website')

    parser.add_argument('url', type=str, help='please input a journal website url')

    args = parser.parse_args()
    url = args.url

    print(pull_doi(url))