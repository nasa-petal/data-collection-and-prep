import ast
import traceback
import time
import argparse
import sys

import pandas as pd

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
    return pd.read_csv(csv_file)

def raw_data_check(df):
    unlabeled_papers = df[df['Functions Level I'].isna()]['Primary lit site']
    print(f'There are {len(unlabeled_papers)} papers without labels')

    duplicate_papers = df[df.duplicated(['Primary lit site'])]['Primary lit site'].drop_duplicates().sort_values()
    print(f'There are {len(duplicate_papers)} duplicate papers')
    print(duplicate_papers)

    print(df.duplicated(subset='Primary lit site', keep='first').sum())

    # Look for commas in the labels
    # Loop through all the records
    papers_with_commas_in_labels = set()
    for index, row in df[['Primary lit site', 'Functions Level I']].iterrows():
        if not isinstance(row['Functions Level I'],float):
            labels_as_string = row['Functions Level I']
            labels = ast.literal_eval(labels_as_string)
            for label in labels:
                if "," in label:
                    papers_with_commas_in_labels.add(row['Primary lit site'])

    if papers_with_commas_in_labels:
        print("**** the following papers have labels with commas in them ****")
        for paper in papers_with_commas_in_labels:
            print(f"    {paper}")
        print("**** *****\n")

def filter_by_lit_site(df, filter_string):
    return df[df['Primary lit site'].str.contains(filter_string, case=True)]

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
                title, doi, abstract, full_doc_link, is_open_access = paper_info
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
        }, ignore_index=True)

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog = sys.argv[0],
                                     description = "scape sites and generate csv with info.")

    # usually "../data/Colleen_and_Alex.csv"
    parser.add_argument('input_csv', type=str, help='input CSV file that needs additional info')
    # usually "Colleen_and_Alex_transformed.csv"
    parser.add_argument('output_csv', type=str, help='output CSV file')
    # usually "Colleen_and_Alex_etl_status.csv"
    parser.add_argument('status_csv', type=str, help='status CSV file')

    parser.add_argument('--n', help='limit the number of journals to this number',
                        default=None, type=int)

    parser.add_argument('--filter', type=str,
                        help='filter based on matching this search string in Primary Lit Site',
                        default=None)

    args = parser.parse_args()

    df = extract(args.input_csv)

    raw_data_check(df)

    if args.filter:
        df = filter_by_lit_site(df, args.filter)

    if args.n:
        df = filter_by_count(df, args.n)

    transformed_df, status_df = transform(df)

    transformed_data_check(transformed_df)

    load(transformed_df, args.output_csv)

    save_status(status_df, args.status_csv)
