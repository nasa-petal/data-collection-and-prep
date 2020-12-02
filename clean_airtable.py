import pandas as pd
df = pd.read_csv('airtable_papers.csv')
print(df.columns)
#Dropping all rows without any URL
df = df[df['Primary lit site'].notna()]

#Cleaning function
def clean_multiple_urls(df):
    rows_lst = []
    for index, row in df.iterrows():
        rows_lst.append(list(row))
        #Retrieving list of URLS, and only operating if it has multiple
        urls = row['Primary lit site'].split('\n')
    
        if len(urls) >= 2:
            rows_lst.remove(list(row))
            #If it has multiple URLS, drop that row for now
            #df = df.drop(index=index)
            #Create new row for each URL with same data in all other columns
            for url in urls:
                if len(url) > 2:
                    data = [row['DOI'], row['Paper title'], row['Abstract'], row['Journal'], url,
                    row['Functions Level I'], row['Functions Level II'], row['Functions Level III- NEW'],
                    row['Functions Level III-OLD'], row['Link to press release']
                    ]
                    #Append new rows to dataframe
                    rows_lst.append(data)
    return pd.DataFrame(rows_lst).drop_duplicates()

df = clean_multiple_urls(df)

#Resetting index
df = df.reset_index()
#Outputting to clean csv
df.to_csv('cleaned_airtable.csv')