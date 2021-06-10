from pymed import PubMed
import pandas as pd

df_jeb = pd.DataFrame(columns=['title', 'abstract'])
df_jeb = df_jeb.convert_dtypes()


pubmed = PubMed(tool="MyTool", email="my@email.address")
query = '("The Journal of experimental biology"[Journal]) AND (("2002/01/01"[Date - Publication] : "3000"[Date - Publication]))'
results = pubmed.query(query, max_results=10000)
for r in results:
    doi = "http://dx.doi.org/" + r.doi if r.doi else ''
    df_jeb = df_jeb.append(
        {'title': r.title,
         'abstract': r.abstract,
         'doi': doi,
         'pmid': f"https://pubmed.ncbi.nlm.nih.gov/{r.pubmed_id}/",
         },
        ignore_index=True)

df_jeb.to_csv("pubmed_titles_abstracts_doi_pmid.csv")

# from pymed import PubMed

# # Create a PubMed object that GraphQL can use to query
# # Note that the parameters are not required but kindly requested by PubMed Central
# # https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
# pubmed = PubMed(tool="MyTool", email="my@email.address")
#
# # Create a GraphQL query in plain text
# query = '(("2018/05/01"[Date - Create] : "3000"[Date - Create])) AND (Xiaoying Xian[Author] OR diabetes)'
#
# # Execute the query against the API
# results = pubmed.query(query, max_results=500)
#
# # Loop over the retrieved articles
# for article in results:
#
#     # Extract and format information from the article
#     article_id = article.pubmed_id
#     title = article.title
#     if article.keywords:
#         if None in article.keywords:
#             article.keywords.remove(None)
#         keywords = '", "'.join(article.keywords)
#     publication_date = article.publication_date
#     abstract = article.abstract
#
#     # Show information about the article
#     print(
#         f'{article_id} - {publication_date} - {title}\nKeywords: "{keywords}"\n{abstract}\n'
#     )