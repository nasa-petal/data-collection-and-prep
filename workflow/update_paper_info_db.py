import ast
import traceback
import time
import argparse
import sys
import datetime
from pathlib import Path
import shutil

from dotenv import load_dotenv

import pandas as pd

from column_definitions import standard_columns, key_mapping

from get_paper_info import get_paper_info, which_literature_site

from workflow_utilities import labels_fix, abstract_fix, extract, filter_by_lit_site, filter_by_count, save_status

def scrape_paper_info(input_record, df_status):
    url = input_record['url']
    print(f"url: {url}")

    start_time = time.time()

    # fix labels
    input_record['label_level_1'] = labels_fix(input_record['label_level_1'])
    input_record['label_level_2'] = labels_fix(input_record['label_level_2'])
    input_record['label_level_3'] = labels_fix(input_record['label_level_3'])

    title = doi = abstract = full_doc_link = ''
    is_open_access = False

    try:
        paper_info = get_paper_info(url)
        if paper_info:
            title, doi, abstract, full_doc_link, is_open_access, is_blocked = paper_info

            # fix abstract
            abstract = abstract_fix(abstract)

            get_paper_info_result = 'no_exception'

            input_record['title'] = title
            input_record['doi'] = doi
            input_record['abstract'] = abstract
            input_record['full_doc_link'] = full_doc_link
            input_record['is_open_access'] = is_open_access
        else:
            get_paper_info_result = 'no_code'
        error_traceback = ""
    except Exception as err:
        get_paper_info_result = 'exception'
        error_traceback = traceback.format_exc()

    scrape_time = time.time() - start_time

    literature_site = which_literature_site(url)
    input_record['literature_site'] = literature_site

    df_status = df_status.append({
        'url': url,
        'literature_site': literature_site,
        'get_paper_info_result': get_paper_info_result,
        'title_len': len(title) if isinstance(title, str) else 0,
        'abstract_len': len(abstract) if isinstance(abstract, str) else 0,
        'doi_len': len(doi) if isinstance(doi, str) else 0,
        'full_doc_link_len': len(full_doc_link) if isinstance(full_doc_link, str) else 0,
        'is_open_access': is_open_access,
        # 'num_labels': len(input_record['label_level_1']),
        'num_labels': len(input_record['label_level_1'].split(',')),
        'error_traceback': error_traceback,
        'scrape_time': scrape_time,
    }, ignore_index=True)

    return input_record, df_status

def update_paper_info_db(df_paper_info_db,n,filter):
    # Need to keep track of the status of each attempt to get paper info
    df_status = pd.DataFrame(columns=['url', 'get_paper_info_result',
                                      'title_len', 'abstract_len', 'doi_len',
                                      'full_doc_link_len', 'is_open_access',
                                      'num_labels',
                                      'error_traceback', 'scrape_time'])
    df_status.astype(int)  # No floats

    i = 0
    for index, row in df_paper_info_db.iterrows():
        if filter and filter != row['literature_site']:
            continue
        if n and i >= n:
            break
        # input_record = dict(zip(standard_columns, row))
        input_record = row.to_dict()
        print(f"{index}: input_record['url']: {input_record['url']}")

        # check to see if anything missing
        if len(input_record['title']) and len(input_record['abstract']) \
                and len(input_record['full_doc_link']) and len(input_record['url']) \
                and len(input_record['doi']):
            print("already complete")
            continue

        # scrape this url
        new_input_record, df_status = scrape_paper_info(input_record, df_status)

        # Loop through the fields and if the same, skip. If different warn and update. If
        #   current was empty, just update
        # for key in standard_columns:
        #     if not matching_record[key]:
        #         matching_record[key] = input_record[key]
        #     else:
        #         if matching_record[key] != input_record[key]:
        #             print(f"Warning! For {input_record['url']} the {key} value changed.")
        #             matching_record[key] = input_record[key]
        # replace?
        print("updating")
        # df_paper_info_db.loc[df_paper_info_db['url'] == input_record['url']] = matching_record
        i = df_paper_info_db[ df_paper_info_db['url'] == input_record['url']].index
        df_paper_info_db.drop(i, inplace=True)
        df_paper_info_db = df_paper_info_db.append(input_record, ignore_index=True)

    return df_paper_info_db, df_status


default_path_to_env = Path( Path.home(), '.petal_env')

parser = argparse.ArgumentParser(prog = sys.argv[0],
                                 description = "scape sites and generate csv with info.")

parser.add_argument('paper_info_csv', type=str, help='main paper info CSV file to be updated')
parser.add_argument('status_csv', type=str, help='status CSV file')

parser.add_argument('-n', help='limit the number of journals to this number',
                    default=None, type=int)

parser.add_argument('--filter', type=str,
                    help='filter based on matching this search string in Primary Lit Site',
                    default=None)

parser.add_argument("--env_path", help = "path to .env file containing API keys",
                    default = default_path_to_env, type = str)

args = parser.parse_args()

load_dotenv(args.env_path)

df_paper_info_db = pd.read_csv(args.paper_info_csv)

# raw_data_check(df)

# if args.filter:
#     df_paper_info_db = filter_by_lit_site(df_paper_info_db, args.filter)
#
# # # Only scrape what needs to be scraped. First see what is in the output csv
# # df = filter_based_on_what_already_has_been_done(df, args.output_csv)
#
# if args.n:
#     df_paper_info_db = filter_by_count(df_paper_info_db, args.n)

# Make a timestamped backup copy
path = Path(args.paper_info_csv)

mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
s = mtime.strftime('%Y%m%d-%H-%M-%S')
p = str(path.with_suffix('')) + '_' + s + path.suffix
shutil.copy2(args.paper_info_csv, p)

df_paper_info_db = df_paper_info_db.fillna("")

# Update and append paper info table
df_paper_info_db, df_status = update_paper_info_db(df_paper_info_db,args.n,args.filter)

df_paper_info_db.to_csv(args.paper_info_csv, index=False)

save_status(df_status, args.status_csv)
