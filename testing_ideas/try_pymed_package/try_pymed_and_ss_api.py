# Use the pymed package to call the PubMed API to get lots of papers from, in this case, JEB

from pymed import PubMed
import pandas as pd
import requests

_REQUESTS_TIMEOUT = 3.0

df_jeb = pd.DataFrame(columns=['title', 'abstract'])
df_jeb = df_jeb.convert_dtypes()

pubmed = PubMed(tool="MyTool", email="my@email.address")
# query = '("The Journal of experimental biology"[Journal]) AND (("2002/01/01"[Date - Publication] : "3000"[Date - Publication]))'
query = '("The Journal of experimental biology"[Journal]) AND (("2002/01/01"[Date - Publication] : "2018/10/10"[Date - Publication]))'
# results = pubmed.query(query, max_results=10000)
results = pubmed.query(query, max_results=100)
for r in results:
    doi = "http://dx.doi.org/" + r.doi if r.doi else ''
    df_jeb = df_jeb.append(
        {'title': r.title,
         'abstract': r.abstract,
         'doi': doi,
         'pmid': f"https://pubmed.ncbi.nlm.nih.gov/{r.pubmed_id}/",
         },
        ignore_index=True)

    ss_api_url = f'https://api.semanticscholar.org/v1/paper/{r.doi}'
    response = requests.get(ss_api_url, timeout=_REQUESTS_TIMEOUT)
    ss_api_results = response.json()
    print('is open access', ss_api_results['is_open_access'])
    if r.title.startswith("Bumb"):
        print(response)
        print('is open access', ss_api_results['is_open_access'])
df_jeb.to_csv("pubmed_titles_abstracts_doi_pmid_100_only.csv")
