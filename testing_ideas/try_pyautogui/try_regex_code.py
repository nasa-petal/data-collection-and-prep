from bs4 import BeautifulSoup
import os, re

# open the HTML saved for https://science.sciencemag.org/content/352/6292/1392, which has a DOI as a string (not href)
html = open(f'{os.getcwd()}/regex_match_in_string.html', "r").read()
soup = BeautifulSoup(html, 'html.parser')

# pattern = re.compile("^10.\d{4,9}/[-._;()/:A-Za-z0-9]+$")
pattern = re.compile("\W10.\d{4,9}/[-._;()/:A-Za-z0-9]+\W")
# pattern = re.compile("(\W|^)10.\d{4,9}/[-._;()/:A-Za-z0-9]+\W",)

doi_1 = ' 10.1126/science.aaf3252 '
doi_1_match = re.search(pattern, doi_1)

doi_2 = '10.1038/ncomms1373'
doi_2_match = re.search(pattern, doi_1)

doi_3 = "test 10.1126/science.aaf3252 test 10.1038/ncomms1373 test"
# doi_3 = "10.1126/science.aaf3252 test 10.1038/ncomms1373"
doi_3_match_findall = re.findall(pattern, doi_3)
doi_3_match_soup = soup.find_all(string=pattern)

print('doi_1 match found!') if doi_1_match else print('no doi_1 match')
print('doi_2 match found!') if doi_2_match else print('no doi_2 match')
print('doi_3 match found using findall!') if doi_3_match_findall else print('no doi_3 match using findall')
print('doi_3 match found using soup!') if doi_3_match_findall else print('no doi_3 match using soup')