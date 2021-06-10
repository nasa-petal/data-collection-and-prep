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
