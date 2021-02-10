import traceback

import pandas as pd

from get_paper_info import get_paper_info, which_journal

class AskNatureLabeledEtl(object):

    def __init__(self):
        self.raw_df = None
        self.transformed_df = None
        self.status_df = None

    def extract(self, csv_file):
        # read from csv into DataFrame
        self.raw_df = pd.read_csv(csv_file)

    def filter(self, url_substring):
        if url_substring:
            self.raw_df = self.raw_df[self.raw_df['Primary lit site'].str.contains(
                url_substring, case=True)]

    def raw_data_check(self):
        # Check for empty labels
        unlabeled_papers = self.raw_df[self.raw_df['Functions Level I'].isna()]['Primary lit site']
        print(f'There are {len(unlabeled_papers)} URLs without labels')
        # with pd.option_context('display.max_rows', None,
        #                        'display.max_columns', None,
        #                        'display.max_colwidth', 100):
        #     print(unlabeled_papers)

        # check for duplicates
        # ????

    def transform(self):
        # Augment data with info via scraping
        self.transformed_df = pd.DataFrame(columns=['title', 'doi', 'abstract', 'labels', 'url',
                                                    'journal',
                                                    'full_doc_link', 'is_open_access'])

        self.status_df = pd.DataFrame(columns=['url', 'journal', 'get_paper_info_result', 'num_labels',
                                               'error_traceback'])
        self.status_df.astype(int)

        for index, row in self.raw_df[['Primary lit site', 'Functions Level I']].iterrows():
            # if index > 20: break
            url, labels = row
            print(f"{index} url: {url}")

            journal = which_journal(url)

            # fix labels
            labels = self.labels_fix(labels)

            try:
                title, doi, abstract, full_doc_link, is_open_access = get_paper_info(url)
                if title:
                    get_paper_info_result = 'success'
                    # fix abstract
                    abstract = self.abstract_fix(abstract)

                    self.transformed_df = self.transformed_df.append({
                        'title': title,
                        'doi': doi,
                        'abstract': abstract,
                        'labels': labels,
                        'url': url,
                        'journal': journal,
                        'full_doc_link': full_doc_link,
                        'is_open_access': is_open_access,
                    }, ignore_index=True)
                else:
                    get_paper_info_result = 'no_code'
                error_traceback = ""
            except Exception as err:
                get_paper_info_result = 'error'
                error_traceback = traceback.format_exc()

            self.status_df = self.status_df.append({
                'url': url,
                'journal': journal,
                'get_paper_info_result': get_paper_info_result,
                'num_labels': len(labels),
                'error_traceback': error_traceback,
            }, ignore_index=True )

    def load(self,csv_file_for_ml):
        self.transformed_df.to_csv(csv_file_for_ml)

    def save_status(self,csv_file_for_status):
        self.status_df.to_csv(csv_file_for_status)

    def print_status(self):
        with pd.option_context('display.max_rows', None,
                               'display.max_columns', None,
                               'display.max_colwidth', 100):
            print(self.status_df)

    def save_summary_status(self, csv_for_summary_status, html_for_summary_status):
        journal_groups = self.status_df.groupby('journal')
        status_summary_df = pd.DataFrame(
            columns=['journal', 'num_papers', 'success', 'error', 'no_code', 'no_labels'])
        for journal, group in journal_groups:
            result_values = group['get_paper_info_result'].value_counts()
            success = result_values.get("success", 0)
            error = result_values.get("error", 0)
            no_code = result_values.get("no_code", 0)
            no_labels = group.query('num_labels == 0').num_labels.count()
            num_papers = group.shape[0]
            status_summary_df = status_summary_df.append(
                {'journal': journal, 'num_papers': num_papers, 'success': success, 'error': error,
                 'no_code': no_code, 'no_labels': no_labels}, ignore_index=True)
            status_summary_df = status_summary_df.sort_values(['num_papers'], ascending=[False])

            # sums = status_summary_df.select_dtypes(include=['int64']).sum().rename('Totals') # Series
            sums = status_summary_df.sum().rename('Totals') #  Series

            row_df = pd.DataFrame([sums])
            status_summary_df = pd.concat([row_df, status_summary_df], ignore_index=True)


            # status_summary_df = pd.concat([sums, status_summary_df[:]]).reset_index(drop=True)


        with pd.option_context('display.max_rows', None,
                               'display.max_columns', None,
                               'display.max_colwidth', 100):
            # print(status_summary_df)
            status_summary_df.to_csv(csv_for_summary_status)
            status_summary_df.to_html(html_for_summary_status)
            status_summary_df.to_html('../docs/asknature_labeled_summary_status.html')


    def abstract_fix(self, abstract):
        if abstract:
            abstract = "".join(abstract.splitlines())  # get abstract on one line
        else:
            abstract = ""
        return abstract

    def labels_fix(self, labels):
        if isinstance(labels, str):
            labels = labels.replace("[", "")
            labels = labels.replace("]", "")
            labels = labels.replace("\'", "")
            labels = labels.split(', ')
        else:
            labels = []
        return labels


etl = AskNatureLabeledEtl()

etl.extract("../data/Colleen_and_Alex.csv")

etl.raw_data_check()

# etl.filter('plos')

etl.transform()

etl.load("Colleen_and_Alex_transformed.csv")

etl.save_status("Colleen_and_Alex_etl_status.csv")

etl.save_summary_status('Colleen_and_Alex_etl_summary_status.csv', 'Colleen_and_Alex_etl_summary_status.html')

