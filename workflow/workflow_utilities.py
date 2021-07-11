import boto3
import pandas as pd
import time
import traceback

from get_paper_info import get_paper_info, which_literature_site

_REQUESTS_TIMEOUT = 3.0 # used as the timeout argument to requests.get calls.

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

def filter_by_lit_site(df, filter_string):
    return df[df['url'].str.contains(filter_string, case=True)]

def filter_by_count(df, count):
    return df.head(count)

def save_status(df, csv_file):
    df.to_csv(csv_file)

def get_mturk_client(environment, aws_profile):
    """
    Create the MTurk client object used to interact with MTurk
    """
    environments = {
        "production": {
            "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
            "preview": "https://www.mturk.com/mturk/preview"
        },
        "sandbox": {
            "endpoint":
                "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
            "preview": "https://workersandbox.mturk.com/mturk/preview"
        },
    }
    mturk_environment = environments[environment]

    session = boto3.Session(profile_name=aws_profile)  # This profile was created using AWS command
    # line tools. Creating that involved using access keys
    client = session.client(
        service_name='mturk',
        region_name='us-east-1',
        endpoint_url=mturk_environment['endpoint'],
    )

    return client, mturk_environment

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
        'num_labels': len(input_record['label_level_1'].split(',')),
        'error_traceback': error_traceback,
        'scrape_time': scrape_time,
    }, ignore_index=True)

    return input_record, df_status
