#!/usr/bin/env python
# coding: utf-8

"""
Given the name of a table in Alex's Airtable, download the information to a CSV file.
"""

from pathlib import Path
import argparse
import os
import sys

import requests
import pandas as pd

from dotenv import load_dotenv

from column_definitions import standard_columns, key_mapping
_REQUESTS_TIMEOUT = 3.0

def convert_columns(input_record):
    # make an empty record
    output_record = dict.fromkeys(standard_columns, '')
    # loop through the keys and look for matches of columns names in the airtable fields
    # if a match and that field is not empty, use that value.
    # Otherwise, leave as empty string
    for output_key in output_record.keys():
        for input_key in key_mapping[output_key]:
            if input_key in input_record and input_record[input_key]:
                output_record[output_key] = input_record[input_key]
                break
    return output_record

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
        response = requests.get(url, params=params, headers=headers, timeout=_REQUESTS_TIMEOUT)
        airtable_response = response.json()
        airtable_records += (airtable_response['records'])
        if 'offset' in airtable_response:
            run = True
            params = (('offset', airtable_response['offset']),)
        else:
            run = False

    airtable_rows = []
    for record in airtable_records:
        converted_columns = convert_columns(record['fields'])
        airtable_rows.append(converted_columns)
    df = pd.DataFrame(airtable_rows)

    return df

if __name__ == "__main__":
    default_path_to_env = Path( Path.home(), '.petal_env')

    parser = argparse.ArgumentParser(prog = sys.argv[0],
                                     description = "get airtable with labeled papers.")
    parser.add_argument("--env_path", help = "path to .env file containing API keys",
                        default = default_path_to_env, type = str)
    parser.add_argument('table', type=str, help='name of Airtable to retrieve')
    parser.add_argument('output_csv', type=str, help='output CSV file')
    args = parser.parse_args()

    load_dotenv(args.env_path)

    table = args.table

    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
    # e.g. 'Colleen%20and%20Alex'
    df = retrieve_airtable_data(table, AIRTABLE_API_KEY)
    
    df.to_csv(args.output_csv)
