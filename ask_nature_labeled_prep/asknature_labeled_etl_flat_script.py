import traceback

import pandas as pd

from get_paper_info import get_paper_info, which_journal

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


### Load ###
raw_df = pd.read_csv("../data/Colleen_and_Alex.csv")

### Data check ###
unlabeled_papers = raw_df[raw_df['Functions Level I'].isna()]['Primary lit site']
print(f'There are {len(unlabeled_papers)} URLs without labels')

### Filter ###
raw_df = raw_df[raw_df['Primary lit site'].str.contains('uchicago', case=True)]

### Transform ###

# Make an empty table for the results of the transform
transformed_df = pd.DataFrame(columns=['title', 'doi', 'abstract', 'labels', 'url',
                                            'journal',
                                            'full_doc_link', 'is_open_access'])

# Need to keep track of the status of each attempt to get paper info
status_df = pd.DataFrame(columns=['url', 'journal', 'get_paper_info_result', 'num_labels',
                                       'error_traceback'])
status_df.astype(int)  # No floats

# Loop through the records to get paper info
for index, row in raw_df[['Primary lit site', 'Functions Level I']].iterrows():
    url, labels = row
    print(f"{index} url: {url}")

    journal = which_journal(url)

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
                'journal': journal,
                'full_doc_link': full_doc_link,
                'is_open_access': is_open_access,
            }, ignore_index=True)
        else:
            get_paper_info_result = 'no_code'
        error_traceback = ""
    except Exception as err:
        get_paper_info_result = 'error'
        error_traceback = traceback.format_exc()

    status_df = status_df.append({
        'url': url,
        'journal': journal,
        'get_paper_info_result': get_paper_info_result,
        'num_labels': len(labels),
        'error_traceback': error_traceback,
    }, ignore_index=True)

### Load ###
transformed_df.to_csv("Colleen_and_Alex_transformed.csv")

### Save status of the process of getting the paper info
status_df.to_csv("Colleen_and_Alex_etl_status.csv")
