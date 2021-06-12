#!/usr/bin/env python
# coding: utf-8

"""
Create a summary of the results in the primary CSV database
"""

import argparse
import sys

import pandas as pd

parser = argparse.ArgumentParser(prog=sys.argv[0],
                                 description="Summarize the contents of the table containing all the paper info and labels.")
parser.add_argument('paper_info_csv', type=str, help='input CSV file containing paper info')
parser.add_argument('summary_csv', type=str, help='output CSV file with summary')
parser.add_argument('summary_html', type=str, help='output HTML file with summary')
args = parser.parse_args()

paper_info_df = pd.read_csv(args.paper_info_csv).fillna('') # get rid of any potential NaNs

literature_site_groups = paper_info_df.groupby('literature_site')
paper_info_summary_df = pd.DataFrame(
    columns=['literature_site', 'num_papers',
             'title', 'abstract', 'doi', 'full_doc_link', 'is_open_access',
             'label_level_1', 'ml_ready', 'labeling_ready'])

paper_info_summary_df = paper_info_summary_df.convert_dtypes()

for literature_site, group in literature_site_groups:
    result_values = group['literature_site'].value_counts() # total count
    label_level_1 = len(group[group.label_level_1.str.len()>0])
    title_success = len(group[group.title.str.len()>0])
    abstract_success = group[group.abstract.str.len()>0].shape[0]
    doi_success = len(group[group.doi.str.len()>0])
    full_doc_link_success = len(group[group.full_doc_link.str.len()>0])
    is_open_access = group.query('is_open_access == True').is_open_access.count()
    num_papers = group.shape[0]

    labeling_ready_mask = (group['title'].str.len() > 0) & \
                          (group['abstract'].str.len() > 0) & \
                          (group['label_level_1'].str.len() == 0)
    labeling_ready = len(group.loc[labeling_ready_mask])

    ml_ready_mask = (group['title'].str.len() > 0) & \
                          (group['abstract'].str.len() > 0) & \
                          (group['label_level_1'].str.len() > 0)
    ml_ready = len(group.loc[ml_ready_mask])

    paper_info_summary_df = paper_info_summary_df.append(
        {'literature_site': literature_site,
         'num_papers': num_papers,
         'title': title_success,
         'abstract': abstract_success,
         'doi': doi_success,
         'full_doc_link': full_doc_link_success,
         'is_open_access': is_open_access,
         'label_level_1': label_level_1,
         'ml_ready': ml_ready,
         'labeling_ready': labeling_ready,
         },
        ignore_index=True)

# sort by number of papers
paper_info_summary_df = paper_info_summary_df.sort_values(['num_papers'], ascending=[False])

# Summary line at the top
sums = paper_info_summary_df.sum().rename('total')
paper_info_summary_df = pd.concat([pd.DataFrame([sums]), paper_info_summary_df[:]]).reset_index(drop = True)

# for some reason the column order gets changed
cols_to_order = ['literature_site',]
new_columns = cols_to_order + (paper_info_summary_df.columns.drop(cols_to_order).tolist())
paper_info_summary_df = paper_info_summary_df[new_columns]
paper_info_summary_df.iat[0,0] = "Totals"

with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.max_colwidth', 100):
    paper_info_summary_df.to_csv(args.summary_csv)
    paper_info_summary_df.to_html(args.summary_html)


