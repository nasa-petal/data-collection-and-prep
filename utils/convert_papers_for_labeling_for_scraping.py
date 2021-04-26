import argparse
import sys
import pandas as pd


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog = sys.argv[0],
                                     description = "transform column names and filter.")

    parser.add_argument('input_csv', type=str, help='input CSV file')
    parser.add_argument('output_csv', type=str, help='output CSV file')

    args = parser.parse_args()

    input_df = pd.read_csv(args.input_csv)

    output_df = pd.DataFrame(columns=['title', 'doi', 'abstract', 'labels', 'Primary lit site',
                                           'literature_site',
                                           'full_doc_link', 'is_open_access'])
    for index, row in input_df.iterrows():
        output_df = output_df.append({
            'title': row['Title'],
            'doi': row['DOI'],
            'Abstract': row['Abstract'],
            'Functions Level I': '',
            'Primary lit site': row['Journal URL'],
            'journal': '',
            'full_doc_link': '',
            'is_open_access': False,
        }, ignore_index=True)

    # Journal URL
    # Abstract
    # Title
    # DOI
    output_df.to_csv(args.output_csv)

