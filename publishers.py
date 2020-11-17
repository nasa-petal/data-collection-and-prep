#Testing script to see who are the top publishers in our Airtable
import pandas as pd

df = pd.read_csv('Papers for Crowdsourcing-Grid view.csv')
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
#print(df['publisher'].unique())
#print(df['publisher'].value_counts()[:20])

print(df[df['publisher'] == 'link']['URL'].values[0])

