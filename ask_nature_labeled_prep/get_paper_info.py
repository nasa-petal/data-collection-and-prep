import random
from urllib.parse import urlparse
import time

import requests
from bs4 import BeautifulSoup

_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
}


# dx, doi, publish, books, empty!, archive, web, 2008, members

def which_literature_site(url):
    # given the url, what is the literature site that it is from, e.g. 'pnas'

    url = url.strip()

    url_components = urlparse(url)
    netloc = url_components.netloc

    literature_site = netloc

    return literature_site

class PaperInfo(object):
    # Abstract class for all of the
    def __init__(self, url):
        self.url = url
        self.html = self.get_html()
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.pdf_link = None

    def get_html(self):
        # use request module to get HTML from the Webpage at self.url
        r = requests.get(self.url, headers = _headers)
        html = r.text
        return html

    def get_title(self):
        # given self.html, get the title
        pass

    def get_doi(self):
        # given self.html, get the doi
        pass

    def get_abstract(self):
        # given self.html, get the abstract
        pass

    def get_full_doc_link(self):
        # given self.html, get the full_doc_link
        pass

    def is_open_access(self):
        if self.pdf_link is '':
            self.pdf_link = self.get_full_doc_link()

        if self.pdf_link is '' or self.pdf_link is None:
            return False

        # stream=True defer downloading the response body
        #   until you access the Response.content attribute
        # Doing things this way makes sure we get all the headers we need
        # calling requests.head didn't always seem to get the full
        #  set of headers
        # See https://requests.readthedocs.io/en/master/user/advanced/ for more info

        with requests.get(self.pdf_link, headers = _headers, stream=True) as r:
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
    def get_title(self):
        # given self.html, get the title
        title = self.soup.find('h1', class_='c-article-title').text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        spans = self.soup.find_all('span', class_='c-bibliographic-information__value')
        for span in spans:
            if 'doi' in span.text:
                doi = span.text.strip()
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
        abstract = self.soup.find(id='Abs1-content', class_='c-article-section__content').text.strip()
        return abstract

    def get_full_doc_link(self):
        # given self.html, get the full_doc_link
        pdf_link = self.url + '.pdf'
        self.pdf_link = pdf_link
        return pdf_link


class PaperInfoJEB(PaperInfo):
    def get_title(self):
        # given self.html, get the title
        title = self.soup.find('div', class_='highwire-cite-title', id='page-title').text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        doi = self.soup.find('span', class_='highwire-cite-metadata-doi highwire-cite-metadata').text
        doi = doi[5:].strip()
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
        abstract = self.soup.find('p', id='p-1').text.strip()
        return abstract

    def get_full_doc_link(self):
        # given self.html, get the full_doc_link
        for a in self.soup.find_all('a', href=True):
            link = a['href']
            if 'pdf' in link:
                if 'jeb.biologists.org' in link:
                    pdf_link = link
        self.pdf_link = pdf_link
        return pdf_link

class PaperInfoSpringer(PaperInfo):
    def get_title(self):
        # given self.html, get the title
        title = self.soup.find('h1', class_='c-article-title').text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        doi = self.soup.find('span', class_='bibliographic-information__value u-overflow-wrap').text.strip()
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
        abstract = self.soup.find('p', class_='Para').text.strip()
        return abstract

    def get_full_doc_link(self):
        # given self.html, get the full_doc_link
        pdf_link = self.url.replace('chapter','content/pdf')+'.pdf'
        self.pdf_link = pdf_link
        return pdf_link


class PaperInfoRSP(PaperInfo):
    def get_title(self):
        # given self.html, get the title
        title = self.soup.find('h1', class_='citation__title').text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        doi = self.soup.find('a', class_='epub-section__doi__text').text.strip()
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
        abstract = self.soup.find('div', class_='abstractSection abstractInFull').text.strip()
        return abstract

    def get_full_doc_link(self):
        # given self.html, get the full_doc_link
        pdf_link = self.url.replace('full', 'pdf')
        self.pdf_link = pdf_link
        return pdf_link


class PaperInfoPNAS(PaperInfo):
    def get_title(self):
        # given self.html, get the title
        title = self.soup.find('h1', class_='highwire-cite-title').text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        doi = self.soup.find('span', class_='highwire-cite-metadata-doi highwire-cite-metadata').text.strip()
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
        abstract = self.soup.find('div', class_='section abstract').find('p').text.strip()
        return abstract

    def get_full_doc_link(self):
        # given self.html, get the full_doc_link
        if self.url[-4:] == 'full':
            pdf_link = self.url + '.pdf'
        else:
            pdf_link = self.url + '.full.pdf'
        self.pdf_link = pdf_link
        return pdf_link


class PaperInfoPubMed(PaperInfo):
    def get_title(self):
        title = self.soup.find(id="full-view-heading").find("h1").text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        doi = ''
        doi_node = self.soup.find('span', class_='identifier doi')
        if doi_node:
            a_node = doi_node.find('a')
            if a_node:
                doi = a_node.text.strip()
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
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
            r = requests.get(full_doc_pre_link, headers= _headers, allow_redirects=True)
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
    def get_title(self):
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

    def get_abstract(self):
        # given self.html, get the abstract
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
    def get_title(self):
        # given self.html, get the title
        title_tag = self.soup.find(class_='citation__title')
        if title_tag:
            title = title_tag.text.strip()
        else:
            title = ''
        return title

    def get_doi(self):
        # given self.html, get the doi
        doi_class = self.soup.find(class_="section__body section__body--article-doi")
        doi = doi_class.find('a').get('href')
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
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
    def get_title(self):
        # given self.html, get the title
        title = ''
        title_node = self.soup.find(class_='wi-article-title article-title-main')
        if title_node:
            title = title_node.text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        doi = ''
        doi_class = self.soup.find(class_='ww-citation-primary')
        if doi_class:
            doi = doi_class.find('a').get('href')
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
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
        time.sleep(random.randint(5, 10))

class PaperInfoScienceDirect(PaperInfo):
    def get_title(self):
        # given self.html, get the title
        title = self.soup.find(class_='title-text').text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        doi_tag = self.soup.find(id='doi-link')
        doi = doi_tag.find('a').get('href')
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
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
        return pdf_link

    def time_delay(self):
        time.sleep(random.randint(5, 10))

    # def is_open_access(self):
    #     if self.pdf_link is '':
    #         self.pdf_link = self.get_full_doc_link()
    #
    #     # stream=True defer downloading the response body
    #     #   until you access the Response.content attribute
    #     # Doing things this way makes sure we get all the headers we need
    #     # calling requests.head didn't always seem to get the full
    #     #  set of headers
    #     # See https://requests.readthedocs.io/en/master/user/advanced/ for more info
    #     with requests.get(self.pdf_link, stream=True) as r:
    #         if not r.ok:
    #             return False
    #         if r.headers['Content-Type'] != 'application/pdf':
    #             return False
    #         if r.headers['content-length'] == 0 :
    #             return False
    #
    #     return True

#
# sciencedirect 133
# science 69
# onlinelibrary 63
# oup 44
# plos 38
# jstor 38
# cell 28
# acs 26
# tandfonline 23
# ncbi 23
# uchicago 21

# pubmed 57   code_to_handle_success: 45, code_to_handle_failed: 12,
# pnas 67  code_to_handle_success: 65, code_to_handle_failed: 2, no_code_to_handle: 0 --- https://www.pnas.org/content/108/24/E198.full  fails
# nature 94 code_to_handle_success: 52, code_to_handle_failed: 42 https://www.nature.com/articles/nature03185 does not work
# jeb 127 code_to_handle_success: 94, code_to_handle_failed: 33
# springer 127 code_to_handle_success: 0, code_to_handle_failed: 127
# royalsocietypublishing 80 code_to_handle_success: 78, code_to_handle_failed: 2


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
}


def get_paper_info(url):
    #Determine the literature site name, and create corresponding object name
    literature_site = which_literature_site(url)

    if literature_site not in paper_info_classes:
        return None
    paper_info_class = paper_info_classes[literature_site]
    paper_info_instance = paper_info_class(url)

    #Retrieiving paper properties
    title = paper_info_instance.get_title()
    doi = paper_info_instance.get_doi()
    abstract = paper_info_instance.get_abstract()
    full_doc_link = paper_info_instance.get_full_doc_link()
    is_open_access = paper_info_instance.is_open_access()

    return title, doi, abstract, full_doc_link, is_open_access
