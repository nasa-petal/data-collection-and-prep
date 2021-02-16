import traceback
import time

import pandas as pd

from get_paper_info import get_paper_info, which_literature_site

def labels_fix(labels):
    '''
    Deal with empty labels and convert them to a list if they are not
    '''
    if isinstance(labels, str):
        labels = labels.replace("[", "")
        labels = labels.replace("]", "")
        labels = labels.replace("\'", "")
        labels = labels.split(', ')
    else:
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

def filter_by_lit_site(df, filter_string):
    return df[df['Primary lit site'].str.contains(filter_string, case=True)]

def filter_by_count(df, count):
    return df.head(count)

def transform(df):
    # Make an empty table for the results of the transform
    transformed_df = pd.DataFrame(columns=['title', 'doi', 'abstract', 'labels', 'url',
                                           'journal',
                                           'full_doc_link', 'is_open_access'])

    # Need to keep track of the status of each attempt to get paper info
    status_df = pd.DataFrame(columns=['url', 'journal', 'get_paper_info_result', 'num_labels',
                                      'error_traceback', 'scrape_time'])
    status_df.astype(int)  # No floats

    # Loop through the records to get paper info
    for index, row in df[['Primary lit site', 'Functions Level I','Abstract']].iterrows():
        url, labels, abstract = row
        print(f"{index} url: {url}")

        start_time = time.time()

        literature_site = which_literature_site(url)

        # continue

        # fix labels
        labels = labels_fix(labels)

        try:
            paper_info = get_paper_info(url)
            if paper_info:
                title, doi, abstract, full_doc_link, is_open_access = paper_info
                get_paper_info_result = 'success'

                # fix abstract
                abstract = abstract_fix(abstract)

                transformed_df = transformed_df.append({
                    'title': title,
                    'doi': doi,
                    'abstract': abstract,
                    'labels': labels,
                    'url': url,
                    'journal': literature_site,
                    'full_doc_link': full_doc_link,
                    'is_open_access': is_open_access,
                }, ignore_index=True)
            else:
                get_paper_info_result = 'no_code'
            error_traceback = ""
        except Exception as err:
            get_paper_info_result = 'error'
            error_traceback = traceback.format_exc()

        scrape_time = time.time() - start_time
        status_df = status_df.append({
            'url': url,
            'journal': literature_site,
            'get_paper_info_result': get_paper_info_result,
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
    df = extract("../data/Colleen_and_Alex.csv")

    raw_data_check(df)

    # df = filter_by_lit_site(df, 'pubmed.ncbi.nlm.nih.gov')
    df = filter_by_lit_site(df, 'www.pnas.org')

    print("filtered data check")
    raw_data_check(df)


    # df = filter_by_count(df, 10)

    transformed_df, status_df = transform(df)

    transformed_data_check(transformed_df)

    load(transformed_df, "Colleen_and_Alex_transformed.csv")

    save_status(status_df, "Colleen_and_Alex_etl_status.csv")
