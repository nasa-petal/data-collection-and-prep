'''
    Download JEB articles for a taxon.
    Simple HTML parser..
    :param previous: neo4j transaction representing a Taxon.
'''
from selenium import webdriver
from bs4      import BeautifulSoup 
from pprint import pprint
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
import time
JEB_LIMIT = 50

# TODO: Add resume feature
# TODO: Add save to json feature

def jeb_search_download(query):
    driver = webdriver.Firefox()
   
    url    = 'https://journals.biologists.com/search-results?page=1&q=' + query
    driver.get(url)    
    
    soup   = BeautifulSoup(driver.page_source, 'html.parser')
    articles = []
    article_divs = [x for x in soup.find_all('div', attrs={'class': 'sri-title customLink al-title'})]
    article_links = ['https://journals.biologists.com/' + a.find(lambda tag:tag.name== 'a' and tag.has_attr('href'))['href'] for a in article_divs]
    next_link = soup.find('a', attrs={'class':'sr-nav-next al-nav-next'})

    while (next_link is not None):
        for article_link in article_links:
            driver.get(article_link)
            article_page = BeautifulSoup(driver.page_source, 'html.parser')
            category     = article_page.find(attrs={'class' : 'article-client_type'}).get_text()
            if category.lower() == 'research article':
                properties = dict()
                properties['url']  = article_link
                properties['title']    = article_page.find(attrs={'class' : 'wi-article-title article-title-main'}).get_text()
                author_divs = article_page.find_all(attrs={'class' : 'al-author-name'})
                author_names = [a.find(lambda tag:tag.name == 'div' and tag.get('class')== ['info-card-name']) for a in author_divs]
                author_names = [a.get_text().lstrip().rstrip() for a in author_names if a]
                properties['authors']  = author_names
                properties['abstract'] = article_page.find(attrs={'class' : 'abstract'}).get_text()
                articles.append(properties)
            driver.execute_script("window.history.go(-1)")

        if next_link:
            driver.find_element_by_link_text("Next").click()
            next_link = soup.find('a', attrs={'class':'sr-nav-next al-nav-next'})

if __name__ == "__main__":
    jeb_search_download('feline')