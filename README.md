# crowdsourcing_papers
Starting with a list of URLs of papers that can be used for crowdsourcing, create a CSV file with the URL, DOI of the paper, Title, Abstract, and if the paper is open access.

Outline
- Export CSV from Airtable
- Extract URLs from CSV
- Get HTML of the Webpage at the URL
- Extract from the HTML ( the code for each these depends on which journal or source )
  - Title
  - DOI
  - Abstract
  - Link to the full document
  - Check to see if the full document is open access
- Put all of this info for each paper into a new CSV that will be used for MTurk

## Usage

`python prepare_mturk_csv.py airtable_papers.csv output.csv`


## File Descriptions

`get_doi.py` Script to pull DOI for any journal website. Includes parsing DOI from the link or from the text.
   - Example: `python get_doi.py 'https://pubmed.ncbi.nlm.nih.gov/19113150/'`
   - Returns: 10.1103/physreve.78.051902

`get_paper_info.py` Pulls Title, DOI, Abstract, Full Document Link, and whether if its Open Access from various journal sites. Instantiate an object of the correct journal class, e.g. for PubMed articles, type in 'pubmed' to create a `PaperInfoPubMed()` class.
  - Title - `.get_title()`
  - DOI - `.get_doi()`
  - Abstract - `.get_abstract()`
  - Full Document Link - `.get_full_doc_link()`
  - Open Accesss? - `.is_open_access()`

## PubMed Scraper

To scrape from PubMed specifically, instantiate a `PaperInfoPubmed()` class. From there, you have access to 
  - Title - `.get_title()`
  - DOI - `.get_doi()`
  - Abstract - `.get_abstract()`
  - Similar Articles - `.get_similar_articles()`


## Tests

`test_get_doi.py` - Tests `get_doi.py` to ensure correct DOIs are found.

`test_get_paper_info.py` - Tests `get_paper_info.py` to ensure correct titles are found.
