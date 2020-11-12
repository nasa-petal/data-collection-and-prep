import requests
from bs4 import BeautifulSoup


def which_journal(url):
    # given the url, what is the journal that it is from, e.g. 'pnas'
    pass

class PaperInfo(object):
    # Abstract class for all of the
    def __init__(self, url):
        self.url = url
        self.html = self.get_html()
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def get_html(self):
        # use request module to get HTML from the Webpage at self.url
        r = requests.get(self.url)
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

    def is_open_access(self, full_doc_link):
        # given full_doc_link, can you get the full PDF from it?
        pass

class PaperInfoPNAS(PaperInfo):
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

    def is_open_access(self, full_doc_link):
        # given full_doc_link, can you get the full PDF from it?
        pass

class PaperInfoPubMed(PaperInfo):
    def get_title(self):
        # given self.html, get the title
        # #full-view-heading > h1
        soup = BeautifulSoup(self.html, 'html.parser')
        # print(soup.find(id="full-view-heading").find("h1").text.strip())
        title = self.soup.find(id="full-view-heading").find("h1").text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        pass

    def get_abstract(self):
        # given self.html, get the abstract
        pass

    def get_full_doc_link(self):
        # given self.html, get the full_doc_link
        pass

    def is_open_access(self, full_doc_link):
        # given full_doc_link, can you get the full PDF from it?
        pass


paper_info_classes = {
    'pnas': PaperInfoPNAS,
    'pubmed': PaperInfoPubMed,
}


def get_paper_info(url):
    journal = which_journal(url)

    paper_info_class = paper_info_classes[journal]

    paper_info_instance = paper_info_class(url)

    title = paper_info_instance.get_title()
    doi = paper_info_instance.get_doi()
    abstract = paper_info_instance.get_abstract()
    full_doc_link = paper_info_instance.get_full_doc_link()
    is_open_access = paper_info_instance.is_open_access(full_doc_link)

    return (title, doi, abstract, full_doc_link, is_open_access)