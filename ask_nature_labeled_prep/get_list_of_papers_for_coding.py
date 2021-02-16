import pprint

import requests
import pandas as pd

def retrieve_airtable_data(table, api_key):
    '''
    Uses airtable API key to request table data from airtable.

    Parameters
    table : string name of the table
    '''
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


if __name__ == "__main__":
    table = 'Colleen%20and%20Alex'
    api_key = 'keypvMblCRCGZeNU4'

    df = retrieve_airtable_data(table, api_key)

    urls = df['Primary lit site']

    search_string = 'plos'

    urls = [ url for url in urls if search_string in url ]
    pprint.pprint(list(urls))