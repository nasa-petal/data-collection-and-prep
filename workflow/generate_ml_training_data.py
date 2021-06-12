#!/usr/bin/env python
# coding: utf-8

"""
Given a CSV file with information about papers, generate another CSV file that has
proper columns and formatting that the machine learning engineer can use to train a model
"""

import argparse
import sys

import pandas as pd

parser = argparse.ArgumentParser(prog=sys.argv[0],
                                 description="generate a training data table using scraped labeled papers.")

parser.add_argument('input_csv', type=str, help='input CSV file containing scraped and labeled paper info')
parser.add_argument('training_csv', type=str, help='output CSV file with training data')
args = parser.parse_args()

transformed_df = pd.read_csv(args.input_csv)

transformed_df = transformed_df.fillna("") # remove the NaNs that sometimes appear in the files

# we only take the records in the DB that have all the fields needed to do ML training.
# we need records with title, abstract, and the level 1 label
ml_df = transformed_df[['title', 'abstract', 'label_level_1', 'doi', 'url']]
mask = (ml_df['title'].str.len() > 0 ) & (ml_df['abstract'].str.len() > 0) & (ml_df['label_level_1'].str.len() > 0)
ml_df = ml_df.loc[mask]

ml_df.to_csv(args.training_csv)
