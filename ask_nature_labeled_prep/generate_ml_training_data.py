import pandas as pd

import numpy as np

transformed_df = pd.read_csv('Colleen_and_Alex_transformed.csv')


# 'title', 'doi', 'abstract', 'labels', 'url',
#                                            'literature_site',
#                                            'full_doc_link', 'is_open_access'

ml_df = transformed_df[['title', 'abstract', 'labels', 'doi', 'url']]
# ml_df = ml_df.query('len(title) > 0 and len(abstract) > 0 and len(labels) > 0')

# mask = (ml_df['title'].str.len() > 0 ) & (ml_df['abstract'].str.len() > 120) & (len(ml_df['labels']) > 0)
mask = (ml_df['title'].str.len() > 0 ) & (ml_df['abstract'].str.len() > 0) & (len(ml_df['labels']) > 0)
ml_df = ml_df.loc[mask]

ml_df.to_csv('Colleen_and_Alex_training_data.csv')
