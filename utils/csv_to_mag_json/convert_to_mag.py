import pandas as pd
import re
import nltk
import string
import json
import requests
from decouple import config
import math
import os
import argparse

# Global Variables
stopwords = nltk.corpus.stopwords.words('english')
special_characters = string.punctuation


def get_arg_parser():
    """Allows arguments to be passed into this program through the terminal.
    Returns:
        argparse.ArgumentParser.parseArgs(): Object containing selected options
    """

    def dir_path(string):
        if os.path.isfile(string):
            return string
        else:
            raise NotADirectoryError(string)

    parser = argparse.ArgumentParser(description="Input document file paths")
    parser.add_argument(
        "csv_path", help="Full path to CSV labeled file", type=dir_path)
    parser.add_argument("output_name", help="Name of output file", type=str)
    return parser.parse_args()


# Define text tokenization and cleaning functions
def clean_text(text: string):
    """Tokenizes and formats strings.
    Args:
        text : string
            A single string.
    Returns:
        list
            List of tokenized words.
    """

    tokenized_text = nltk.tokenize.word_tokenize(text)
    cleaned_text = [re.sub(r"([^A-z0-9]|\\u....)","", text.lower(
    )) for text in tokenized_text if text not in special_characters and text not in stopwords]
    cleaned_text = [text for text in cleaned_text if text != ""]

    return cleaned_text


def clean_labels(labels: list):
    """Reformats labels into more model friendly formats.
    Args:
        labels : list
            A formatted list of biomimicry labels.
    Returns:
        list
            List of properly formatted labels.
    """

    clean_labels = [re.sub("\s", "_", label).lower()
                    for label in labels]
    return clean_labels


def get_mag_data(dataframe: pd.DataFrame):
    """Uses DOIs from the imported DataFrame to make queries to Microsoft Academic.
    Args:
        dataframe : pd.DataFrame
            Dataframe of our labeled data.
    Returns:
        Tuple
            list
                A list consisting of the papers pulled from MAG in a JSON format.
            list
                A list consisting of only the papers DOIs.
    """

    # Define GET parameters
    url = "https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate"
    batch_size = 10
    params = {
        "subscription-key": config("MAG_KEY"),
        "expr": "",
        "attributes": "Id,F.FN,VFN,AA.AuId,RId,Ti,AW,DOI",
        "count": batch_size
    }

    # Make DOI requests in batches of 20
    paper_dois = [f"DOI='{doi.upper()}'" for doi in dataframe["doi"]]
    total_size = math.ceil(len(paper_dois)/batch_size)
    mag_res = []

    for i in range(total_size):
        print("Progress: {0:0.2%}".format(i/total_size), end="\r")
        doi_list = "OR(" + \
            ", ".join(paper_dois[i*batch_size:(i*batch_size)+batch_size]) + ")"
        params["expr"] = doi_list
        r = requests.get(url, params=params)

        if (r.status_code == 200):
            temp_response = json.loads(r.text)["entities"]
            mag_res += temp_response

    mag_dois = list(map(lambda paper: paper.get("DOI", ""), mag_res))
    return (mag_res, mag_dois)


def convert_to_json(dataframe: pd.DataFrame, mag_res: list, mag_dois: list):
    """ Creates a list of json objects by merging MAG data with our own dataframe.
    Args:
        dataframe : pd.DataFrame
            Dataframe of our labeled data.
        mag_res : list
            A list of MAG papers each in JSON format.
        mag_dois : list
            A list of MAG dois.
    Returns:
        list
            List of objects containing our labeled data merged with MAG data.
    """

    # Define list for newly formatted data
    golden_jsons = []

    # Convert dataframe to json format
    for index, row in dataframe.iterrows():
        mag_index = mag_dois.index(
            row["doi"].upper()) if row["doi"].upper() in mag_dois else -1
        mag_paper = (mag_index >= 0 and mag_res[mag_index]) or {}
        temp_dict = {}

        if (mag_index >= 0):
            temp_dict["paper"] = mag_paper["Id"]
            temp_dict["mag"] = mag_paper.get("F", []) and list(
                map(lambda field: field["FN"], mag_paper["F"]))
            temp_dict["venue"] = [mag_paper.get("VFN", None)]
            temp_dict["author"] = mag_paper.get("AA", []) and list(
                map(lambda field: field["AuId"], mag_paper["AA"]))
            temp_dict["reference"] = mag_paper.get("RId", [])
            temp_dict["abstract"] = mag_paper.get("AW", (row["abstract"] and clean_labels(
                row["abstract"])) or [])  # and clean_text(row["abstract"])
        else:
            temp_dict["paper"] = ""
            temp_dict["mag"] = []
            temp_dict["venue"] = (eval(row["journal"]) if (len(row["journal"]) and row["journal"][0] =="[") else row["journal"]) or []
            temp_dict["author"] = []
            temp_dict["reference"] = []
            # (row["abstract"] and clean_labels(row["abstract"])) or []
            temp_dict["abstract"] = []

        temp_dict["petalID"] = index
        temp_dict["doi"] = row["doi"].upper()
        temp_dict["title"] = (row["title"] and clean_text(row["title"])) or []
        temp_dict["level1"] = row["label_level_1"] and clean_labels(
            eval(row["label_level_1"]))
        temp_dict["level2"] = row["label_level_2"] and clean_labels(
            eval(row["label_level_2"]))
        temp_dict["level3"] = row["label_level_3"] and clean_labels(
            eval(row["label_level_3"]))
        temp_dict["url"] = row["url"]
        temp_dict["fullDocLink"] = row["full_doc_link"]
        temp_dict["isOpenAccess"] = row["is_open_access"]
        golden_jsons.append(temp_dict)

    return golden_jsons


if __name__ == "__main__":
    args = get_arg_parser()
    dataframe = pd.read_csv(args.csv_path)
    dataframe = dataframe.fillna("")
    (mag_res, mag_dois) = get_mag_data(dataframe)
    golden_jsons = convert_to_json(dataframe, mag_res, mag_dois)

    # Write json data to a json file
    with open(f"{args.output_name}.json", "a") as golden_file:
        golden_file.write("[\n")
        golden_size = len(golden_jsons)

        for index in range(golden_size):
            golden_file.write("\t")
            golden_file.write(json.dumps(golden_jsons[index]))

            if(index < golden_size):
                golden_file.write(",\n")
