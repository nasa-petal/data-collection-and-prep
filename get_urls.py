import pandas as pd


def get_urls(input_csv_filename):
    df = pd.read_csv(input_csv_filename)
    urls = df['URL'].tolist()
    return urls
