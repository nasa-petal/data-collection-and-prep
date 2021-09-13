#A script that pulls DOI from any journal publication website
import requests
from bs4 import BeautifulSoup
import re
import argparse
import sys

def pull_doi(url):
    # r = requests.get(url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}

    r = requests.get(url,headers=headers)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    doi = ''

    # qqq = soup.find_all('a')
    # zzz = len(qqq)
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
        # need to use a more sophisticated doi regex
        #   https://www.crossref.org/blog/dois-and-matching-regular-expressions/
        #   https://www.regextester.com/93795
        doi = soup(text=re.compile(r'/^10.\d{4,9}/[-._;()/:A-Z0-9]+$/i'))
        
        if len(doi) == 0:
            doi = soup(text=re.compile(r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![\"&\'<>])\S)+)\b'))
        if len(doi) == 0:
            doi = re.search(r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![\"&\'<>])\S)+)\b', url).groups()
            
        if len(doi):
            doi = doi[0].strip()
            #removing all characters before first number in DOI
            doi = re.search('[0-9].*', doi)[0]
        else:
            doi =""

    return doi

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pull DOI from Any Journal Website')

    parser.add_argument('url', type=str, help='please input a journal website url')

    args = parser.parse_args()
    url = args.url

    print(pull_doi(url))