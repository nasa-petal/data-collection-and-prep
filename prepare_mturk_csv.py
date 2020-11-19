import argparse
import sys

import get_urls
import get_paper_info
import write_mturk_csv



parser = argparse.ArgumentParser(description='Prepare MTurk CSV Command Line Tool')

parser.add_argument('input_csv', type=str, help='CSV file from Airtable')

parser.add_argument('output_csv', type=str, help='CSV file for ML')

args = parser.parse_args(sys.argv)  # sys.argv is used if argv parameter is None
input_csv_filename = args.input_csv
output_csv_filename = args.output_csv

urls = get_urls.get_urls(input_csv_filename)

info_on_papers = []
for url in urls:
    
    title, doi, abstract, full_doc_link, is_open_access = get_paper_info.get_paper_info(url)
    info_on_papers.append((title, doi, abstract, full_doc_link, is_open_access))

write_mturk_csv.write_mturk_csv(info_on_papers, output_csv_filename)

