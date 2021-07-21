import pandas as pd
import numpy as np
import json
import argparse
import os


def get_args():
    """ Allows users to input arguments
    Returns:
        argparse.ArgumentParser.parse_args
            Object containing options input by user
    """
    def isFile(string: str):
        if os.path.isfile(string):
            return string
        else:
            raise

    parser = argparse.ArgumentParser()
    parser.description = "Counts the amount of MAG, and MeSH terms in a JSON newline delmited file."
    parser.add_argument("input_file", type=isFile,
                        help="Path to JSON newline delimited file")
    return parser.parse_args()


def load_dataframe(input_path: str):
    """ Loads json newline delimited file into a dataframe and trims down to mesh and mag terms
        Args:
            input_path: str
                Full or relative path to the input file
        Returns:
            pandas.DataFrame
                Dataframe containing only mag and mesh terms
    """
    paper_list = []
    with open(input_path, "r") as cleaned_file:
        for line in cleaned_file:
            paper_list.append(json.loads(line))

    dataframe = pd.DataFrame(paper_list)
    termsdataframe = dataframe[["mag", "mesh"]]
    return termsdataframe


def convert_to_counts(termsdataframe: pd.DataFrame):
    """ Adds boolean columns to the dataframe representing the presence of mag or mesh terms
        Args:
            termsdataframe: pd.DataFrame
                Dataframe containing only mesh or mag terms
        Returns:
            pd.DataFrame
                Dataframe containing boolean values dictating the presence of mesh or mag terms
    """
    termsdataframe["both"] = termsdataframe.apply(
        lambda row: len(row["mag"]) > 0 and len(row["mesh"]) > 0, axis=1)
    termsdataframe["mesh_only"] = termsdataframe.apply(
        lambda row: len(row["mesh"]) > 0 and len(row["mag"]) == 0, axis=1)
    termsdataframe["mag_only"] = termsdataframe.apply(
        lambda row: len(row["mag"]) > 0 and len(row["mesh"]) == 0, axis=1)
    termsdataframe["none"] = termsdataframe.apply(
        lambda row: len(row["mag"]) == 0 and len(row["mesh"]) == 0, axis=1)
    return termsdataframe


if __name__ == "__main__":
    args = get_args()
    print(args.input_file)
    dataframe = load_dataframe(args.input_file)
    dataframe = convert_to_counts(dataframe)
    print("Mesh Terms Only: {}".format(
        dataframe["mesh_only"].value_counts()[True]))
    print("Mag Terms Only: {}".format(
        dataframe["mag_only"].value_counts()[True]))
    print("Both: {}".format(dataframe["both"].value_counts()[True]))
    print("None: {}".format(dataframe["none"].value_counts()[True]))
