import pandas as pd

import argparse
import sys

parser = argparse.ArgumentParser(prog=sys.argv[0],
                                 description="generate a training data table using scraped labeled papers.")

# usually "../data/Colleen_and_Alex.csv"
parser.add_argument('input_csv', type=str, help='input CSV file containing scraped and labeled paper info')
# usually "Colleen_and_Alex_transformed.csv"
parser.add_argument('training_csv', type=str, help='output CSV file with training data')

args = parser.parse_args()

# 'Colleen_and_Alex_transformed.csv'
transformed_df = pd.read_csv(args.input_csv)

transformed_df = transformed_df.fillna("")

# 'title', 'doi', 'abstract', 'labels', 'url',
#                                            'literature_site',
#                                            'full_doc_link', 'is_open_access'

ml_df = transformed_df[['title', 'abstract', 'label_level_1', 'doi', 'url']]
# ml_df = ml_df.query('len(title) > 0 and len(abstract) > 0 and len(labels) > 0')

# mask = (ml_df['title'].str.len() > 0 ) & (ml_df['abstract'].str.len() > 120) & (len(ml_df['labels']) > 0)
# mask = (ml_df['title'].str.len() > 0 ) & (ml_df['abstract'].str.len() > 0) & (len(ml_df['label_level_1']) > 0)
mask = (ml_df['title'].str.len() > 0 ) & (ml_df['abstract'].str.len() > 0) & (ml_df['label_level_1'].str.len() > 0)
ml_df = ml_df.loc[mask]

# ml_df.to_csv('Colleen_and_Alex_training_data.csv')
ml_df.to_csv(args.training_csv)
