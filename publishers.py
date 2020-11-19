#Run script but after filtering by publishers first
import pandas as pd
import get_paper_info

df = pd.read_csv('airtable_papers.csv')
df = df[df.URL.notnull()]

def which_journal(row):
    # given the url, what is the journal that it is from, e.g. 'pnas'
    url = row['URL']
    if 'www' in url:
        publisher = url.split('.')[1]
    else:
        publisher = url.split('.')[0].split('//')[1]

    return publisher

df['publisher'] = df.apply(which_journal, axis=1)

publishers = [
    'pnas',
    'pubmed',
    'nature',
    'jeb',
    'springer',
    'rsp'
]

df = df[df['publisher'].isin(publishers)]

df['URL'] = df.apply(lambda x: x['URL'].split()[0].strip(), axis=1)
#need to clean urls for all papers, only take first one, and remove all text after last /, only numbers at end of url
df.to_csv('filtered_papers.csv')
filtered = pd.read_csv('filtered_papers.csv')
urls = filtered['URL'].values
info_on_papers = []
for url in urls:
    print(url)
    try:
        title, doi, abstract, full_doc_link, is_open_access = get_paper_info.get_paper_info(url)
        info_on_papers.append((url, title, doi, abstract, full_doc_link, is_open_access))
    except:
        continue

output = pd.DataFrame(info_on_papers, columns=['url', 'title', 'doi', 'abstract', 'full_doc_link', 'is_open_access']).to_csv('output.csv')
