import pandas as pd
df = pd.read_csv('airtable_papers.csv')

#Dropping all rows without any URL
df = df[df['URL'].notna()]

#Cleaning function
def clean_multiple_urls(df):
    for index, row in df.iterrows():
        #Retrieving list of URLS, and only operating if it has multiple
        urls = row['URL'].split(' ')
        if len(urls) >= 2:
            #If it has multiple URLS, drop that row for now
            df = df.drop(index=index)
            #Create new row for each URL with same data in all other columns
            for url in urls:
                data = [row['DOI'], row['Paper title'], row['Abstract'], row['Journal'], url,
                    row['Functions'], row['PDF'], row['Press release']]
                #Append new rows to dataframe
                df.append(data)
    return 

clean_multiple_urls(df)
#Resetting index
df = df.reset_index()
#Outputting to clean csv
df.to_csv('cleaned_airtable.csv')