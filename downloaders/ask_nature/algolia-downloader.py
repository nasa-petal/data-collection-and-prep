import pandas as pd
import algoliasearch.search_client
import datetime
import argparse


def get_args():

    parser = argparse.ArgumentParser(
        description="Download all biomimicry papers from AskNature modified this month.")
    parser.add_argument("output_file", type=str,
                        help="Name of output CSV file")
    parser.add_argument("app_id", type=str,
                        help="Algolia App ID")
    parser.add_argument("api_key", type=str,
                        help="API Key for Algolia")
    args = parser.parse_args()
    return args


def request_papers(app_id, api_key):

    # Get timestamp of beginning of current month
    current_date = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0)
    earliest_timestamp = current_date.timestamp()

    # Initialize Algolia search client
    client = algoliasearch.search_client.SearchClient.create(
        app_id, api_key)
    index = client.init_index("asknature_searchable_posts")

    # Search client for biomimicry papers modified this month
    asknature_response = index.search(
        "filters: post_type_label:'Biological Strategies' AND post_modified > {}".format(earliest_timestamp))["hits"]

    return asknature_response


def process_papers(asknature_response):

    # Define sub-methods to extract dois, urls an labels
    def get_doi(paper, index, sources):
        return ""

    def get_url(index, sources):
        return sources["source_link"][index]

    def get_labels(paper):
        tax_functions = paper["taxonomies_hierarchical"]["function"]
        level_1_labels = [label.split(" > ")[0]
                          for label in tax_functions.get("lvl0", [])]
        level_2_labels = [label.split(" > ")[1]
                          for label in tax_functions.get("lvl1", [])]
        level_3_labels = [label.split(" > ")[2]
                          for label in tax_functions.get("lvl2", [])]
        return [level_1_labels, level_2_labels, level_3_labels]

    # Convert papers into the current PeTaL csv format and output a dataframe
    formatted_papers = []

    for paper in asknature_response:
        sources = paper.get("reference_sources",
                            False) or paper.get("sources", {})
        ref_count = len(sources.get("source_link", []))
        for i in range(ref_count):
            paper_object = {}
            paper_object["doi"] = get_doi(paper, i, sources)
            paper_object["url"] = get_url(i, sources)
            paper_object["label_level_1"], paper_object["label_level_2"], paper_object["label_level_3"] = get_labels(
                paper)
            formatted_papers.append(paper_object)

    ask_dataframe = pd.DataFrame(formatted_papers)

    return ask_dataframe


if (__name__ == "__main__"):
    args = get_args()
    papers = request_papers(args.app_id, args.api_key)
    asknature_dataframe = process_papers(papers)
    asknature_dataframe.to_csv(args.output_file + ".csv")
