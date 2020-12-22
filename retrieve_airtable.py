import requests
import pandas as pd

# table = 'Papers%20for%20Labelling%20v3'
table = 'Colleen%20and%20Alex'

def retrieve_airtable_data(table):
    '''
    Uses airtable API key to request table data from airtable.
    
    Parameters
    table : string name of the table
    '''
    api_key = 'XXXXX'
    headers = {
        "Authorization": "Bearer %s" % api_key,
    }
    
    url = 'https://api.airtable.com/v0/appmifYhoEdnfPIbU/%s' % table
    params = ()
    airtable_records = []
    run = True
    while run:
        response = requests.get(url, params=params, headers=headers)
        airtable_response = response.json()
        airtable_records += (airtable_response['records'])
        if 'offset' in airtable_response:
            run = True
            params = (('offset', airtable_response['offset']),)
        else:
            run = False

    airtable_rows = []
    for record in airtable_records:
        airtable_rows.append(record['fields'])
    df = pd.DataFrame(airtable_rows)

    return df
#
df = retrieve_airtable_data(table)
table = table.replace('%20', '_')
df.to_csv('%s.csv' % table)