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

def labels_fix(labels):
    '''
    Deal with empty labels and convert them to a list if they are not
    '''
    if not isinstance(labels, str):
        labels = []
    return labels

def abstract_fix( abstract):
    '''
    Some abstracts will come back in multiple lines. Want one line?
    '''
    if abstract:
        abstract = "".join(abstract.splitlines())  # get abstract on one line
    else:
        abstract = ""
    return abstract

def extract(csv_file):
    return pd.read_csv(csv_file, na_filter=False)

def raw_data_check(df):
    unlabeled_papers = df[df['label_level_1'].isna()]['url']
    print(f'There are {len(unlabeled_papers)} papers without labels')

    duplicate_papers = df[df.duplicated(['url'])]['url'].drop_duplicates().sort_values()
    print(f'There are {len(duplicate_papers)} duplicate papers')
    print(duplicate_papers)

    print(df.duplicated(subset='url', keep='first').sum())

    # Look for commas in the labels
    # Loop through all the records
    papers_with_commas_in_labels = set()
    for index, row in df[['url', 'label_level_1']].iterrows():
        if not isinstance(row['label_level_1'],float):
            labels_as_string = row['label_level_1']
            labels = ast.literal_eval(labels_as_string)
            for label in labels:
                if "," in label:
                    papers_with_commas_in_labels.add(row['url'])

    if papers_with_commas_in_labels:
        print("**** the following papers have labels with commas in them ****")
        for paper in papers_with_commas_in_labels:
            print(f"    {paper}")
        print("**** *****\n")

def filter_by_lit_site(df, filter_string):
    return df[df['url'].str.contains(filter_string, case=True)]

def filter_by_count(df, count):
    return df.head(count)

def transform(df):
    # Make an empty table for the results of the transform
    transformed_df = pd.DataFrame(columns=['title', 'doi', 'abstract', 'labels', 'url',
                                           'literature_site',
                                           'full_doc_link', 'is_open_access'])

    # Need to keep track of the status of each attempt to get paper info
    status_df = pd.DataFrame(columns=['url', 'literature_site', 'get_paper_info_result',
                                      'title_len', 'abstract_len', 'doi_len',
                                      'pdf_len', 'is_open_access',
                                      'num_labels',
                                      'error_traceback', 'scrape_time'])
    status_df.astype(int)  # No floats

    # Loop through the records to get paper info
    for index, row in df[['Primary lit site', 'Functions Level I','Abstract']].iterrows():
        url, labels, abstract = row
        # if pd.isnull(labels):
        #     labels = ''
        print(f"{index} url: {url}")

        start_time = time.time()

        literature_site = which_literature_site(url)

        # continue
        title = doi = abstract = full_doc_link = ''
        is_open_access = False

        # fix labels
        labels = labels_fix(labels)

        try:
            paper_info = get_paper_info(url)
            if paper_info:
                title, doi, abstract, full_doc_link, is_open_access, is_blocked = paper_info
                if is_blocked:
                    get_paper_info_result = 'blocked'
                else:
                    get_paper_info_result = 'no_exception'

                    # fix abstract
                    abstract = abstract_fix(abstract)

                    transformed_df = transformed_df.append({
                        'title': title,
                        'doi': doi,
                        'abstract': abstract,
                        'labels': labels,
                        'url': url,
                        'literature_site': literature_site,
                        'full_doc_link': full_doc_link,
                        'is_open_access': is_open_access,
                    }, ignore_index=True)
            else:
                get_paper_info_result = 'no_code'
            error_traceback = ""
        except Exception as err:
            get_paper_info_result = 'exception'
            error_traceback = traceback.format_exc()

        scrape_time = time.time() - start_time

        status_df = status_df.append({
            'url': url,
            'literature_site': literature_site,
            'get_paper_info_result': get_paper_info_result,
            'title_len': len(title) if isinstance(title,str) else 0,
            'abstract_len': len(abstract) if isinstance(abstract,str) else 0,
            'doi_len': len(doi) if isinstance(doi,str) else 0,
            'full_doc_link_len': len(full_doc_link) if isinstance(full_doc_link,str) else 0,
            'is_open_access': is_open_access,
            'num_labels': len(labels),
            'error_traceback': error_traceback,
            'scrape_time': scrape_time,
        }, ignore_index=True, na_filter= False)

    return transformed_df, status_df

def load(df, csv_file):
    df.to_csv(csv_file)

def save_status(df, csv_file):
    df.to_csv(csv_file)

def transformed_data_check(df):
    print('Number of empty cells in the columns')
    for name in df.columns:
        c = (df[name] == '').sum()
        print(f'{name}: {c}')

    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.max_colwidth', 100):
        print(df.describe())

# def filter_based_on_what_already_has_been_done(input_df, output_csv):
#     # does the output csv exist? I not, no filtering
#     if not Path(output_csv).exists():
#         return input_df
#     df_exists = pd.read_csv(output_csv)
#
#     # make a new empty one
#     new_df = pd.DataFrame(columns=input_df.columns)
#
#     # Loop through the input df
#     for index, row in input_df.iterrows():
#         _, _, journal, url, labels, level_2, level_3_new, level_3_old, link_press, doi, title, abstract = row
#
#         # check to see if the url matches one in the existing df
#         matches = df_exists.loc[df_exists['url'] == url]
#
#         if not matches.empty :
#             if len(matches) > 1:
#                 raise(ValueError, "Do not know what to do with more than one match")
#             # check to see if we have good values
#             # ~~~~~~~~!!!!!!!!!!!!!! need to handle nan's also
#             if len(matches['doi']) and len(matches['title']) and len(matches['abstract']) and len(matches['full_doc_link']):
#                 continue
#
#         # Otherwise add it to the list of pages to scrape
#         new_df = new_df.append(row,ignore_index=True)
#
#     return new_df


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
        'num_labels': len(input_record['label_level_1']),
        'error_traceback': error_traceback,
        'scrape_time': scrape_time,
    }, ignore_index=True)

    return input_record, df_status

def update_and_append_paper_info_table(df_input, df_paper_info_db):

    # Need to keep track of the status of each attempt to get paper info
    df_status = pd.DataFrame(columns=['url', 'get_paper_info_result',
                                      'title_len', 'abstract_len', 'doi_len',
                                      'full_doc_link_len', 'is_open_access',
                                      'num_labels',
                                      'error_traceback', 'scrape_time'])
    df_status.astype(int)  # No floats

    for index, row in df_input.iterrows():
        # input_record = dict(zip(standard_columns, row))
        input_record = row.to_dict()

        print(f"{index}: input_record['url']: {input_record['url']}")
        # look in df_output for a matching doi
        #    !!!! comes back as Nan
        matching_record = df_paper_info_db.loc[df_paper_info_db['url'] == input_record['url']]

        if not matching_record.empty :
            if len(matching_record) > 1:
                raise(ValueError, "Do not know what to do with more than one match")

            # Need to check to see if scraping is needed
            matching_record = matching_record.fillna("").to_dict('records')[0]
            if len(matching_record['title']) and len(matching_record['abstract']) \
                and len(matching_record['full_doc_link']) and len(matching_record['url']) \
                and len(matching_record['doi']) :
                print("already complete")
                continue

            # scrape this url
            input_record, df_status = scrape_paper_info(input_record, df_status)

            # Loop through the fields and if the same, skip. If different warn and update. If
            #   current was empty, just update
            for key in standard_columns:
                if not matching_record[key]:
                    matching_record[key] = input_record[key]
                else:
                    if matching_record[key] != input_record[key]:
                        print(f"Warning! For {input_record['url']} the {key} value changed.")
                        matching_record[key] = input_record[key]
            # replace?
            print("updating")
            # df_paper_info_db.loc[df_paper_info_db['url'] == input_record['url']] = matching_record
            i = df_paper_info_db[ df_paper_info_db['url'] == input_record['url']].index
            df_paper_info_db.drop(i, inplace=True)
            df_paper_info_db = df_paper_info_db.append(input_record, ignore_index=True)
        else:
            # scrape this url
            print("new url")
            input_record, df_status = scrape_paper_info(input_record, df_status)
            df_paper_info_db = df_paper_info_db.append(input_record, ignore_index=True)

    return df_paper_info_db, df_status

if __name__ == "__main__":

    default_path_to_env = Path( Path.home(), '.petal_env')

    parser = argparse.ArgumentParser(prog = sys.argv[0],
                                     description = "scape sites and generate csv with info.")

    # usually "../data/Colleen_and_Alex.csv"
    parser.add_argument('input_csv', type=str, help='input CSV file that needs additional info')
    # usually "Colleen_and_Alex_transformed.csv"
    parser.add_argument('output_csv', type=str, help='output CSV file')
    # usually "Colleen_and_Alex_etl_status.csv"
    parser.add_argument('status_csv', type=str, help='status CSV file')

    parser.add_argument('-n', help='limit the number of journals to this number',
                        default=None, type=int)

    parser.add_argument('--filter', type=str,
                        help='filter based on matching this search string in Primary Lit Site',
                        default=None)

    parser.add_argument("--env_path", help = "path to .env file containing API keys",
                        default = default_path_to_env, type = str)

    parser.add_argument('--new_db', action='store_true', default=False, dest='new_db',
                        help="create new empty db csv file.")

    args = parser.parse_args()

    load_dotenv(args.env_path)

    df = extract(args.input_csv)

    # raw_data_check(df)

    if args.filter:
        df = filter_by_lit_site(df, args.filter)

    # # Only scrape what needs to be scraped. First see what is in the output csv
    # df = filter_based_on_what_already_has_been_done(df, args.output_csv)

    if args.n:
        df = filter_by_count(df, args.n)

    if args.new_db:
        df_paper_info_db = pd.DataFrame(columns=standard_columns +['literature_site'])
    else:
        # Make a timestamped backup copy
        path = Path(args.output_csv)

        mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
        s = mtime.strftime('%Y%m%d-%H-%M-%S')
        p = str(path.with_suffix('')) + '_' + s + path.suffix
        shutil.copy2(args.output_csv, p)

        df_paper_info_db = pd.read_csv(args.output_csv)

    df_paper_info_db = df_paper_info_db.fillna("")

    # Update and append paper info table
    df_paper_info_db, df_status = update_and_append_paper_info_table(df, df_paper_info_db)

    df_paper_info_db.to_csv(args.output_csv, index=False)

    # transformed_df, status_df = transform(df)
    #
    # transformed_data_check(transformed_df)
    #
    # load(transformed_df, args.output_csv)
    #
    save_status(df_status, args.status_csv)
