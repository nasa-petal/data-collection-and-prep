import sys
import argparse

import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description="convert csv file to html file.")

    parser.add_argument('input_csv', type=str, help='input CSV file')
    parser.add_argument('output_html', type=str, help='output HTML file')

    args = parser.parse_args()

    input_df = pd.read_csv(args.input_csv)

    input_df.to_html(args.output_html)

