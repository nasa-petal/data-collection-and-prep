#  See if we can get paper info using just a two step process and only simple scraping:
#     1. Use Jerry Qian's function to look for DOI links in a Web page
#     2. If successful getting DOI, use the Semantic Search API to get the rest of the
#          paper info that we want
#
#     Print out the results to see how successful we are

import pandas as pd

import requests
from bs4 import BeautifulSoup
import re
import argparse
import os
import datetime
from urllib.parse import urlparse
import time

def get_args():
    """Allows arguments to be passed into this program through the terminal.
    Returns:
        arguments: Object containing selected responses to given options
    """

    def dir_path(string):
        if os.path.isfile(string):
            return string
        else:
            raise NotADirectoryError(string)

    def truthy_value(string):
        if string.lower() in ["yes", "y", "true"]:
            return True
        else:
            return False

    parser = argparse.ArgumentParser(description="Input document file paths")
    parser.add_argument("--path", "-p",
                        help=r"Full path to text file contiaining urls: C:\..\..\urls.txt",
                        default="./urls.txt", type=dir_path)
    parser.add_argument("--overwrite", "-o",
                        help=r"Overwrite existing error_logs. Defaults to false.",
                        default="false", type=truthy_value)
    return parser.parse_args()


def pull_doi(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}

    try:
        r = requests.get(url, headers=headers, timeout=4.0)
    except:
        return ''
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    doi = ''

    # Pulling first DOI from href
    for a in soup.find_all('a', href=True):
        link = a['href']
        if 'doi.org' in link:
            try:
                doi = link.split('doi.org/')[1]
            except:
                doi = ''
            break

    # Pulling first DOI from text
    # Example: https://jeb.biologists.org/content/223/20/jeb226654
    # DOI not embedded in a href, but can only be pulled by searching the text
    if len(doi) == 0:
        # need to use a more sophisticated doi regex
        #   https://www.crossref.org/blog/dois-and-matching-regular-expressions/
        #   https://www.regextester.com/93795

        try:
            doi = soup(text=re.compile(r'/^10.\d{4,9}/[-._;()/:A-Z0-9]+$/i'))[0].strip()

        except Exception as error:
            # Log errors
            with open("error_logs.txt", "a") as error_log:
                error_log.write(datetime.datetime.now().strftime(r"%Y/%m/%d @ %H:%M:%S"))
                error_log.write("\n")
                error_log.write("URL: {}\n".format(url))
                error_log.write("{}\n\n".format(error))

        # removing all characters before first number in DOI
        search_result = re.search('[0-9].*', doi)
        # doi = search_result[0]
        if search_result:
            doi = search_result[0]
        else:
            doi = ''

    if doi:
        doi = "http://dx.doi.org/" + doi

    return doi

def get_paper_info_from_ss(doi):
    url_components = urlparse(doi)
    time.sleep(1.0)
    path = url_components.path # e.g. '/article/10.1007%2Fs002270000466'
    ss_api_url = f'https://api.semanticscholar.org/v1/paper{path}'
    try:
        response = requests.get(ss_api_url, timeout=4.0)
    except:
        response = None
    if response and response.ok:
        ss_api_query_results = response.json()
    else:
        ss_api_query_results = None

    if ss_api_query_results:
        title = ss_api_query_results['title']
        abstract = ss_api_query_results['abstract']
    else:
        abstract = ''
        title = ''

    return title, abstract

df_alex_and_colleen = pd.read_csv("../../data/colleen_and_alex_raw.csv")
df_papers_for_labeling = pd.read_csv("../../data/papers_for_labeling_v3_raw.csv")

urls = list(df_alex_and_colleen['url']) + list(df_papers_for_labeling['url'])

# print(urls)
print(f"total number of papers: {len(urls)}")
doi_count = 0
title_count = 0
url_count = 0

bad_urls = open("bad_urls.txt", "w")
for url in urls:
    print(f"getting info on {url}")
    url_count += 1
    doi = pull_doi(url)
    if doi:
        doi_count += 1
        title, abstract = get_paper_info_from_ss(doi)
    else:
        title, abstract = '', ''
        bad_urls.write(f"{url}\n")
    if title and abstract:
        title_count += 1
    print(url, doi, title, abstract)
    print(f"url_count: {url_count}, doi_count: {doi_count}, title_count: {title_count}")

print(f"doi count: {doi_count}")
print(f"title count: {title_count}")
bad_urls.close()
