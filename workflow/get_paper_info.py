"""
The code that does the collecting of information about a paper.
It uses a combination of Web scraping and APIs
"""
import random
from urllib.parse import urlparse
import time
import os

import requests
from bs4 import BeautifulSoup

_REQUESTS_TIMEOUT = 3.0

_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
}

def which_literature_site(url):
    # given the url, what is the literature site that it is from, e.g. 'pnas'
    url = url.strip()
    url_components = urlparse(url)
    netloc = url_components.netloc
    literature_site = netloc

    return literature_site

class PaperInfo(object):

    # Abstract class for all of the other classes in this file
    def __init__(self, url, scrape_page = True):
        self.time_delay()
        self.url = url
        self.doi = None
        self.blocked = False
        if scrape_page:
            self.html = self.get_html()
            self.blocked = self.check_if_blocked(self.html)
            if not self.blocked:
                self.soup = BeautifulSoup(self.html, 'html.parser')
                self.doi = self.get_doi()
                self.use_ss_api()
        else: # get DOI from url and then use site API, like Springer
            self.doi = self.get_doi()
            self.query_using_api()
        self.pdf_link = None

    def use_ss_api(self):
        url_components = urlparse(self.doi)
        path = url_components.path # e.g. '/article/10.1007%2Fs002270000466'
        ss_api_url = f'https://api.semanticscholar.org/v1/paper{path}'
        response = requests.get(ss_api_url, timeout=_REQUESTS_TIMEOUT)
        if response.ok:
            self.ss_api_query_results = response.json()
        else:
            self.ss_api_query_results = None

    def get_title(self):
        if self.ss_api_query_results:
            return self.ss_api_query_results['title']
        else:
            return self.get_title_using_scraping()

    def get_abstract(self):
        if self.ss_api_query_results:
            return self.ss_api_query_results['abstract']
        else:
            return self.get_abstract_using_scraping()

    def check_if_blocked(self, html):
        return 'not a robot' in html

    def is_blocked(self):
        return self.blocked

    def get_html(self):
        # use request module to get HTML from the Webpage at self.url
        r = requests.get(self.url, headers = _headers, timeout=_REQUESTS_TIMEOUT)
        html = r.text
        return html

    def get_title_using_scraping(self):
        # given self.html, get the title
        pass

    def get_doi(self):
        # given self.html, get the doi
        pass

    def get_abstract_using_scraping(self):
        # given self.html, get the abstract
        pass

    def get_full_doc_link(self):
        # given self.html, get the full_doc_link
        pass

    def is_open_access(self):
        if self.pdf_link == '':
            self.pdf_link = self.get_full_doc_link()

        if self.pdf_link == '' or self.pdf_link is None:
            return False

        # stream=True means defer downloading the response body
        #   until you access the Response.content attribute
        # Doing things this way makes sure we get all the headers we need
        # calling requests.head didn't always seem to get the full
        #  set of headers
        # See https://requests.readthedocs.io/en/master/user/advanced/ for more info
        with requests.get(self.pdf_link, headers = _headers, stream=True, timeout=_REQUESTS_TIMEOUT) as r:
            if not r.ok:
                return False
            content_type = r.headers['Content-Type']
            if not ( content_type.startswith('application/pdf') or content_type.startswith('text/html') ):
                return False
            if 'content-length' in r.headers and r.headers['content-length'] == 0 :
                return False

        return True

    def time_delay(self):
        time.sleep(0.5)

class PaperInfoNature(PaperInfo):
    def get_title_using_scraping(self):
        title = self.soup.find('h1', class_='c-article-title').text.strip()
        return title

    def get_doi(self):
        spans = self.soup.find_all('span', class_='c-bibliographic-information__value')
        for span in spans:
            if 'doi' in span.text:
                doi = span.text.strip()
        return doi

    def get_abstract_using_scraping(self):
        abstract = self.soup.find(id='Abs1-content', class_='c-article-section__content').text.strip()
        return abstract

    def get_full_doc_link(self):
        pdf_link = self.url + '.pdf'
        self.pdf_link = pdf_link
        return pdf_link

class PaperInfoJEB(PaperInfo):
    def get_title_using_scraping(self):
        title = self.soup.find('h1', class_='wi-article-title article-title-main').text.strip()
        return title

    def get_doi(self):
        doi = self.soup.find('div', class_='citation-doi').find('a').get('href')
        return doi

    def get_abstract_using_scraping(self):
        abstract = self.soup.find('section', class_='abstract').text.strip()
        return abstract

    def get_full_doc_link(self):
        pdf_link = self.soup.find('a', class_='article-pdfLink')['href']
        pdf_link = 'https://journals.biologists.com' + pdf_link
        self.pdf_link = pdf_link
        return pdf_link

    def time_delay(self):
        time.sleep(random.randint(20, 40))

class PaperInfoRSP(PaperInfo):
    def get_title_using_scraping(self):
        title = self.soup.find('h1', class_='citation__title').text.strip()
        return title

    def get_doi(self):
        doi = self.soup.find('a', class_='epub-section__doi__text').text.strip()
        return doi

    def get_abstract_using_scraping(self):
        abstract = self.soup.find('div', class_='abstractSection abstractInFull').text.strip()
        return abstract

    def get_full_doc_link(self):
        pdf_link = self.url.replace('full', 'pdf')
        self.pdf_link = pdf_link
        return pdf_link

class PaperInfoPNAS(PaperInfo):
    def get_title_using_scraping(self):
        title = self.soup.find('h1', class_='highwire-cite-title').text.strip()
        return title

    def get_doi(self):
        doi = self.soup.find('span', class_='highwire-cite-metadata-doi highwire-cite-metadata').text.strip()
        return doi

    def get_abstract_using_scraping(self):
        abstract = self.soup.find('div', class_='section abstract').find('p').text.strip()
        return abstract

    def get_full_doc_link(self):
        if self.url[-4:] == 'full':
            pdf_link = self.url + '.pdf'
        else:
            pdf_link = self.url + '.full.pdf'
        self.pdf_link = pdf_link
        return pdf_link

class PaperInfoPubMed(PaperInfo):
    def get_title_using_scraping(self):
        title = self.soup.find(id="full-view-heading").find("h1").text.strip()
        return title

    def get_doi(self):
        doi = ''
        doi_node = self.soup.find('span', class_='identifier doi')
        if doi_node:
            a_node = doi_node.find('a')
            if a_node:
                doi = a_node.text.strip()
        return doi

    def get_abstract_using_scraping(self):
        abstract = ''
        abstract_node = self.soup.find('div', class_='abstract-content selected')
        if abstract_node:
            paragraph_node = abstract_node.find('p')
            if paragraph_node:
               abstract = paragraph_node.text.strip()
        return abstract

    def get_similar_articles(self):
        articles = self.soup.find('ul', class_='articles-list', id="similar-articles-list").findAll('span',
                                            class_="docsum-journal-citation full-journal-citation")

        dois = []
        for article in articles:
            doi = article.text
            doi = doi.split('doi: ')[1].split(' Epub')[0]
            dois.append(doi)
        return dois

    def get_full_doc_link(self):

        full_doc_link = ''
        full_text_node = self.soup.find(class_='full-text-links-list')
        if full_text_node:
            full_doc_pre_link = full_text_node.find('a').get('href')
            r = requests.get(full_doc_pre_link, headers= _headers, allow_redirects=True, timeout=_REQUESTS_TIMEOUT)
            if r.ok:
                soup = BeautifulSoup(r.text, 'html.parser')
                full_text_node = soup.find(class_='pdf-download')
                if full_text_node:
                    full_doc_link_relative = full_text_node.get('href')
                    from urllib.parse import urljoin
                    full_doc_link = urljoin(r.url, full_doc_link_relative)

        self.pdf_link = full_doc_link
        return full_doc_link

class PaperInfoPLOS(PaperInfo):
    def get_title_using_scraping(self):
        title_node = self.soup.find(id='artTitle')
        if title_node:
            title = title_node.text.strip()
        else:
            title = ''
        return title

    def get_doi(self):
        doi_node = self.soup.find(id='artDoi')
        if doi_node:
            doi = doi_node.find('a').get('href')
        else:
            doi = ''
        return doi

    def get_abstract_using_scraping(self):
        abstract = ''
        abstract_node = self.soup.find(class_='abstract-content')
        if abstract_node:
            paragraph_nodes = abstract_node.find_all('p')  # this is a list
            for paragraph_node in paragraph_nodes:
                abstract += ' ' + paragraph_node.text.strip()
        return abstract

    def get_full_doc_link(self):
        pdf_node = self.soup.find(id='downloadPdf')
        if pdf_node :
            pdf_url = 'https://journals.plos.org' + pdf_node['href']
        else:
            pdf_url = ''
        self.pdf_link = pdf_url
        return pdf_url

class PaperInfoUChicago(PaperInfo):
    def get_title_using_scraping(self):
        title_tag = self.soup.find(class_='citation__title')
        if title_tag:
            title = title_tag.text.strip()
        else:
            title = ''
        return title

    def get_doi(self):
        doi_class = self.soup.find(class_="section__body section__body--article-doi")
        doi = doi_class.find('a').get('href')
        return doi

    def get_abstract_using_scraping(self):
        try:
            abstract = self.soup.find(class_='abstractSection abstractInFull').text.strip()
        except:
            abstract = ""
        return abstract

    def get_full_doc_link(self):
        pdf_class = self.soup.find(class_='ctrl--primary ctrl--full-text ctrl')
        if not pdf_class:
            pdf_class = self.soup.find(class_='ctrl--primary ctrl--pdf ctrl')
        if pdf_class:
            pdf = 'https://www.journals.uchicago.edu/' + pdf_class.get('href')
        else:
            pdf = ''
        return pdf

class PaperInfoOUP(PaperInfo):
    def get_title_using_scraping(self):
        title = ''
        title_node = self.soup.find(class_='wi-article-title article-title-main')
        if title_node:
            title = title_node.text.strip()
        return title

    def get_doi(self):
        doi = ''
        doi_class = self.soup.find(class_='ww-citation-primary')
        if doi_class:
            doi = doi_class.find('a').get('href')
        return doi

    def get_abstract_using_scraping(self):
        try:
            abstract_class = self.soup.find(class_='abstract')
            abstract = abstract_class.find(class_='chapter-para').text.strip()
        except:
            abstract = ""
        return abstract

    def get_full_doc_link(self):
        try:
            pdf_class = self.soup.find(class_='al-link pdf article-pdfLink')
            pdf_url = 'https://academic.oup.com/' + pdf_class.get('href')
        except:
            pdf_url = ""
        return pdf_url

    def time_delay(self):
        time.sleep(random.randint(20, 40))

class PaperInfoScienceDirect(PaperInfo):

    def get_title_using_scraping(self):
        title = self.soup.find(class_='title-text').text.strip()
        return title

    def get_doi(self):
        doi_tag = self.soup.find(id='doi-link')
        doi = doi_tag.find('a').get('href')
        return doi

    def get_abstract_using_scraping(self):
        abstract = ''
        abstract_tag = self.soup.find(class_='abstract author')
        if abstract_tag:
            abstract_div = abstract_tag.find('div')
            abstract_paras = abstract_div.find_all('p')
            for i in abstract_paras:
                abstract += i.text.strip()
        return abstract

    def get_full_doc_link(self):
        pdf_link = ''
        get_access = self.soup.find(class_='pdf-download-label-short u-hide-from-lg')
        if get_access.text.strip() != 'Get Access':
            pdf_link = self.url
            if 'abs/' in pdf_link:
                pdf_link = pdf_link.replace('abs/', '')
            if '?via%3Dihub' in pdf_link:
                pdf_link = pdf_link.split('?via%3Dihub', 1)[0]
            pdf_link = pdf_link + '/pdfft'
        self.pdf_link = pdf_link
        print(f"pdf_link: {pdf_link}")
        return pdf_link


class PaperInfoSpringer(PaperInfo):
    base_api_url = "http://api.springernature.com/meta/v2/json"

    def __init__(self, url):
        super().__init__(url, scrape_page=False)

    def get_doi(self):
        # use the URL to get the DOI. Ex,
        # https://link.springer.com/article/10.1007%2Fs11692-009-9069-4?LI=true
        # https://doi.org/10.1007%2Fs11692-009-9069-4
        if self.doi:
            return self.doi

        doi = 'https://doi.org/'  # base of DOI
        doi += self.url.split('chapter/')[-1] if 'chapter' in self.url else \
        self.url.split('article/')[-1]

        # fixing up some parts of the DOI url
        if 'LI=true' in doi:
            doi = doi.split('?LI=true')[0]

        elif '%28' in doi:
            doi = doi.replace('%2F', '/').replace('%28', '(').replace('%29', ')')

        elif '#' in doi:
            doi = doi.split('#')[0]

        self.doi = doi
        return doi

    def query_using_api(self):
        doi_query = self.doi.split('.org/')[1]
        query = f'doi:"{doi_query}"'  # quotes are needed around the DOI for some requests to work

        SPRINGER_API_KEY = os.getenv("SPRINGER_API_KEY")
        if not SPRINGER_API_KEY:
            raise (ValueError, "SPRINGER_API_KEY not available")

        params = {"q": query, "api_key": SPRINGER_API_KEY}
        # Have to do it this way because otherwise requests encodes the colon in the query parameter
        payload_str = "&".join("%s=%s" % (k, v) for k, v in params.items())
        response = requests.get(self.base_api_url, params=payload_str)

        self.query_results = response.json()
        return

    def get_title(self):
        title = self.query_results['records'][0]['title']
        return title

    def get_abstract(self):
        abstract = self.query_results['records'][0]['abstract']
        return abstract

    def get_full_doc_link(self):
        # some links direct to PDF, others direct to original URL
        pdf_link = ''
        return pdf_link

class PaperInfoScienceMag(PaperInfo):
    def get_title_using_scraping(self):
        title_tag = self.soup.find(class_='highwire-cite-title')
        if title_tag:
            title = title_tag.text.strip()
        else:
            title = self.soup.find(class_='article__headline').text.strip()
        return title

    def get_doi(self):
        doi = 'https://doi.org/' + self.soup.find(class_='meta-line').text.strip().split("DOI: ")[1]
        self.doi = doi
        return doi

    def get_abstract_using_scraping(self):
        abstract = ''

        abstract_tag_1 = self.soup.find(class_='section abstract')
        abstract_tag_2 = self.soup.find(class_='section summary')

        if abstract_tag_1:
            abstract = abstract_tag_1.find('p').text.strip()

        elif abstract_tag_2:
            abstract = abstract_tag_2.find('p').text.strip()

        return abstract

    def get_full_doc_link(self):
        return None

class PaperInfoWiley(PaperInfo):
    def get_title_using_scraping(self):
        title = self.soup.find(class_='citation__title').text.strip()
        return title

    def get_doi(self):
        doi = self.soup.find(class_='epub-doi').get('href')
        self.doi = doi
        return doi

    def get_abstract_using_scraping(self):
        abstract = ''
        abstract_tag_1 = self.soup.find(class_='article-section__content en main')  # most common tag to find abstracts
        abstract_tag_2 = self.soup.find(class_='graphical-abstract')  # for abstracts that also contain images
        abstract_tag_3 = self.soup.find(class_='article-section__content fr main')  # least common tag for abstracts

        if abstract_tag_1:
            abstract_paras = abstract_tag_1.find_all('p')  # this abstract tag contains many useful paragraphs
            for paragraph in abstract_paras:  # in some articles, there is a <table> tag nested within the <p> tag
                found_table = paragraph.find('table')  # first search to see if there is a <table> tag
                if found_table:
                    found_table.decompose()  # if there is a table, remove the <table> tag that is nested in the <p>
                abstract += paragraph.text.strip()  # add any other non-table paragraphs to the scraped abstract
        elif abstract_tag_2:
            abstract = abstract_tag_2.text.strip()
        elif abstract_tag_3:
            abstract = abstract_tag_3.text.strip()

        return abstract

    def get_full_doc_link(self):
        pdf_link = ''
        info_tag = self.soup.find(
            class_='doi-access-container clearfix')  # this tag can tell us if an article is open access
        if 'Free Access' in info_tag.text.strip():
            pdf_link = 'https://sfamjournals.onlinelibrary.wiley.com' + self.soup.find(
                class_='coolBar__ctrl pdf-download').get('href')

        return self.pdf_link

class PaperInfoDxDoi(PaperInfo):
    def get_doi(self):
        url_components = urlparse(self.url)
        doi = url_components.path # e.g. '/article/10.1007%2Fs002270000466'
        self.doi = doi
        return doi

class PaperInfoScienceJSTOR(PaperInfo):
    def get_title(self):
        title = self.soup.find(class_='title-font').text.strip()
        return title

    def get_doi(self):
        doi = ''
        doi_tag = self.soup.find(class_='doi')
        if doi_tag:
            doi = doi_tag.get('href')
        return doi

    def get_abstract(self):
        abstract = self.soup.find(class_='summary-paragraph').text.strip()
        return abstract

    def get_full_doc_link(self):
        pdf_class = self.soup.find(class_='primary-access')
        pdf_link = 'https://jstor.org' + pdf_class['href']
        self.pdf_link = pdf_link
        return pdf_link

paper_info_classes = {
    'www.pnas.org': PaperInfoPNAS,
    'pubmed.ncbi.nlm.nih.gov': PaperInfoPubMed,
    'www.nature.com': PaperInfoNature,
    'jeb.biologists.org': PaperInfoJEB,
    'link.springer.com': PaperInfoSpringer,
    'royalsocietypublishing.org': PaperInfoRSP,
    'journals.plos.org': PaperInfoPLOS,
    'academic.oup.com': PaperInfoOUP,
    'www.journals.uchicago.edu': PaperInfoUChicago,
    'www.sciencedirect.com': PaperInfoScienceDirect,
    'science.sciencemag.org': PaperInfoScienceMag,
    'onlinelibrary.wiley.com': PaperInfoWiley,
    'dx.doi.org': PaperInfoDxDoi,
    'www.jstor.org': PaperInfoScienceJSTOR,
}

def get_paper_info(url):
    # Determine the literature site name, and create corresponding object name
    literature_site = which_literature_site(url)

    if literature_site not in paper_info_classes:
        return None
    paper_info_class = paper_info_classes[literature_site]
    paper_info_instance = paper_info_class(url)

    if paper_info_instance.is_blocked():
        title = doi = abstract = full_doc_link = ''
        is_open_access = False
    else:
        # Retrieiving paper properties
        title = paper_info_instance.get_title()
        doi = paper_info_instance.get_doi()
        abstract = paper_info_instance.get_abstract()
        full_doc_link = paper_info_instance.get_full_doc_link()
        is_open_access = paper_info_instance.is_open_access()

    print(f"title: {title}\ndoi: {doi}\nabstract: {abstract}")
    return title, doi, abstract, full_doc_link, is_open_access, paper_info_instance.is_blocked()