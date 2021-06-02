'''
    Download JEB articles for a taxon.
    Simple HTML parser..
    :param previous: neo4j transaction representing a Taxon.
'''
from selenium import webdriver
from bs4      import BeautifulSoup 
from requests import get
from pprint import pprint
JEB_LIMIT = 50


def jeb_search_download(query):

    def process_section(section):
        paragraphs = section.find_all('p')
        return '\n'.join(p.get_text() for p in paragraphs)
    

    url    = 'https://journals.biologists.com/search-results?page=1&q=' + query
    result = get(url)

    soup   = BeautifulSoup(result.content, 'html.parser')
    articles = []
    article_links = ['https://jeb.biologists.org' + x.get('href') for x in soup.find_all('a', attrs={'class': 'sri-figure-title'})]
    i = 0
    for article_link in article_links:
        try:
            if i == JEB_LIMIT:
                break
            article_page = BeautifulSoup(get(article_link).content, 'html.parser')
            category     = article_page.find(attrs={'class' : 'highwire-cite-category'}).get_text()
            if category == 'Research Article':
                properties = dict()
                properties['url']  = article_link
                properties['title']    = article_page.find(attrs={'class' : 'highwire-cite-title'}).get_text()
                properties['authors']  = article_page.find(attrs={'class' : 'highwire-cite-authors'}).get_text()
                article_page = article_page.find(attrs={'class' : 'fulltext-view'})
                sections = [process_section(section) for section in article_page.find_all(attrs={'class' : 'section'})]
                properties['abstract'] = sections[0]
                properties['intro']    = sections[1]
                properties['methods']  = sections[2]
                properties['results']  = sections[3]
                properties['content']  = '\n'.join(sections[1:])
                i += 1
        except AttributeError:
            pass

if __name__ == "__main__":
    jeb_search_download('feline')