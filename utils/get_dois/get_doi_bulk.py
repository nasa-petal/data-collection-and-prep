#A script that pulls DOI from any journal publication website
import requests
from bs4 import BeautifulSoup
import re
import argparse
import sys
import os
import datetime


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
    parser.add_argument("--path", "-p", help=r"Full path to text file contiaining urls: C:\..\..\urls.txt",
                        default="./urls.txt", type=dir_path)
    parser.add_argument("--overwrite", "-o", help=r"Overwrite existing error_logs. Defaults to false.",
                        default="false", type=truthy_value)
    return parser.parse_args()


def pull_doi(url):

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
        # need to use a more sophisticated doi regex
        #   https://www.crossref.org/blog/dois-and-matching-regular-expressions/
        #   https://www.regextester.com/93795
       
        try:
            doi = soup(text=re.compile(r'/^10.\d{4,9}/[-._;()/:A-Z0-9]+$/i'))[0].strip()
        
        except Exception as error:
            # Log errors
            with open("error_logs", "a") as error_log:
                error_log.write(datetime.datetime.now().strftime(r"%Y/%m/%d @ %H:%M:%S"))
                error_log.write("\n")
                error_log.write("URL: {}\n".format(url))
                error_log.write("{}\n\n".format(error))

        #removing all characters before first number in DOI
        doi = re.search('[0-9].*', doi)[0]

    return doi

if __name__ == "__main__":
    args = get_args()

    if args.overwrite:
        with open("./error_logs.txt", "w") as error_logs:
            error_logs.write("")
            error_logs.close()

    with open(args.path, "r") as url_text_file:
        url_list = url_text_file.read().splitlines()
        url_text_file.close()
    
    dois = []
    count = 0
    total = len(url_list)

    for url in url_list:
        count += 1
        try:
            doi = pull_doi(url)
        except:
            doi = "error"
        dois.append(doi)
        print("Progress: {0:0.2%}".format(count/total), end = "\r")

    with open("new_dois.txt", "w") as doi_txt:
        for doi in dois:
            doi_txt.write(doi)
            doi_txt.write("\n")
        doi_txt.close()