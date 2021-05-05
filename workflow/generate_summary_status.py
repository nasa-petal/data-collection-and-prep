import pandas as pd
import argparse
import sys

parser = argparse.ArgumentParser(prog=sys.argv[0],
                                 description="take the result of the individual scrape attempts and summarize the results.")

# usually "../data/Colleen_and_Alex.csv"
parser.add_argument('status_csv', type=str, help='input CSV file containing status info')
# usually "Colleen_and_Alex_transformed.csv"
parser.add_argument('summary_csv', type=str, help='output CSV file with summary')
# usually "Colleen_and_Alex_etl_status.csv"
parser.add_argument('summary_html', type=str, help='output HTML file with summary')

args = parser.parse_args()

# 'Colleen_and_Alex_etl_status.csv'
status_df = pd.read_csv(args.status_csv)

literature_site_groups = status_df.groupby('literature_site')
status_summary_df = pd.DataFrame(
    columns=['literature_site', 'num_papers', 'no_exception', 'exception', 'no_code',
             'title_success', 'abstract_success', 'doi_success', 'full_doc_link_success', 'is_open_access',
             'no_labels', 'ml_ready', 'avg_scrape_time'])
for literature_site, group in literature_site_groups:
    result_values = group['get_paper_info_result'].value_counts()
    no_exception = result_values.get("no_exception", 0)
    exception = result_values.get("exception", 0)
    no_code = result_values.get("no_code", 0)
    no_labels = group.query('num_labels == 0').num_labels.count()
    title_success = group.query('title_len > 0').title_len.count()
    abstract_success = group.query('abstract_len > 0').abstract_len.count()
    doi_success = group.query('doi_len > 0').doi_len.count()
    full_doc_link_success = group.query('full_doc_link_len > 0').full_doc_link_len.count()
    is_open_access = group.query('is_open_access == True').is_open_access.count()
    num_papers = group.shape[0]
    avg_scrape_time = group.scrape_time.mean()

    ml_ready = group.query('title_len > 0 and abstract_len > 0 and num_labels > 0').shape[0]

    status_summary_df = status_summary_df.append(
        {'literature_site': literature_site,
         'num_papers': num_papers,
         'no_exception': no_exception,
         'exception': exception,
         'no_code': no_code,
         'title_success': title_success,
         'abstract_success': abstract_success,
         'doi_success': doi_success,
         'full_doc_link_success': full_doc_link_success,
         'is_open_access': is_open_access,
         'no_labels': no_labels,
         'avg_scrape_time': avg_scrape_time,
         'ml_ready': ml_ready,
         },
        ignore_index=True)

# sort by number of papers
status_summary_df = status_summary_df.sort_values(['num_papers'], ascending=[False])

# Get mean of the scrape times
avg_scrape_time_total = status_summary_df["avg_scrape_time"].mean()

# Summary line at the top
sums = status_summary_df.sum().rename('total')
status_summary_df = pd.concat([pd.DataFrame([sums]), status_summary_df[:]]).reset_index(drop = True)

# status_summary_df.loc[0, 'avg_scrape_time'] = avg_scrape_time_total

# status_summary_df.iloc[0, status_summary_df.columns.get_loc('avg_scrape_time')] = avg_scrape_time_total



# for some reason the column order gets changed
cols_to_order = ['literature_site',]
new_columns = cols_to_order + (status_summary_df.columns.drop(cols_to_order).tolist())
status_summary_df = status_summary_df[new_columns]
status_summary_df.iat[0,0] = "Totals"
status_summary_df.iat[0,status_summary_df.columns.get_loc('avg_scrape_time')] = avg_scrape_time_total

with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.max_colwidth', 100):
    status_summary_df.to_csv(args.summary_csv)
    status_summary_df.to_html(args.summary_html)


