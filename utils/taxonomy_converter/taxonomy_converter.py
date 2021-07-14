import argparse
import pandas as pd
import convert_labels


def get_args():
    parser = argparse.ArgumentParser(
        description='Prepare CSV Command Line Tool')
    parser.add_argument('input_csv', type=str, help='CSV file from Airtable')
    parser.add_argument('output_csv', type=str, help='Updated CSV file')
    args = parser.parse_args()

    return args


def get_function_map(input_csv_filename):
    # returns function map as a list of 3 lists (lvl 1, lvl 2, and lvl 3 functions)
    df = pd.read_csv(input_csv_filename)
    list_of_lists = [df["Level I"].tolist(), df["Level II"].tolist(),
                     df["Level III"].tolist()]
    return list_of_lists


def get_labels(input_csv_filename):

    def labels_to_list(label_list):
        new_list = []

        for label in label_list:
            eval_list = eval(label)
            new_list.append(eval_list)

        return new_list

    # returns list of lists of strings (labels), with each inner list corresponding to one paper
    df = pd.read_csv(input_csv_filename)
    all_bio_functions = []
    all_bio_functions.append(labels_to_list(df["label_level_1"].tolist()))
    all_bio_functions.append(labels_to_list(df["label_level_2"].tolist()))
    all_bio_functions.append(labels_to_list(df["label_level_3"].tolist()))

    return all_bio_functions


def prepare_csv(input_csv_filename, function_map_csv):

    multi_level_labels = get_labels.get_labels(input_csv_filename)
    df = pd.read_csv(input_csv_filename)
    function_map = get_function_map(function_map_csv)

    for index in df.index:
        new_functions = convert_labels.convert_labels(function_map,
                                                      [
                                                          multi_level_labels[0][index],
                                                          multi_level_labels[1][index],
                                                          multi_level_labels[2][index]
                                                      ])

        df.loc[index, "label_level_1"] = str(new_functions[0])
        df.loc[index, "label_level_2"] = str(new_functions[1])
        df.loc[index, "label_level_3"] = str(new_functions[2])

    return df


if (__name__ == "__main__"):

    args = get_args()
    function_map = "function_map.csv"
    converted_dataframe = prepare_csv(args.input_csv, function_map)
    converted_dataframe.to_csv(args.output_csv, index=False)
