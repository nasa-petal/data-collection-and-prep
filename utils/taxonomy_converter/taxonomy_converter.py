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
    df.fillna("", inplace=True)
    for column in df.columns:
        df[column] = df[column].str.lower()
    
    list_of_lists = [df["Level I"].tolist(), df["Level II"].tolist(),
                     df["Level III"].tolist(), df["Alevel I"].tolist(), df["Alevel II"].tolist(),
                     df["Alevel III"].tolist()]
    return list_of_lists


def get_labels(input_csv_filename):

    def labels_to_list(label_list):
        new_list = []

        for label_set in label_list:
            if pd.isna(label_set):
                new_list.append([])
                continue
            eval_list = eval(label_set)
            new_list.append([label.lower() for label in eval_list])

        return new_list

    # returns list of lists of strings (labels), with each inner list corresponding to one paper
    df = pd.read_csv(input_csv_filename)
    all_bio_functions = []
    all_bio_functions.append(labels_to_list(df["label_level_1"].tolist()))
    all_bio_functions.append(labels_to_list(df["label_level_2"].tolist()))
    all_bio_functions.append(labels_to_list(df["label_level_3"].tolist()))

    return all_bio_functions


def prepare_csv(input_csv_filename, function_map_csv):

    multi_level_labels = get_labels(input_csv_filename)
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
        df.loc[index, "ask_label_level_1"] = str(new_functions[3])
        df.loc[index, "ask_label_level_2"] = str(new_functions[4])
        df.loc[index, "ask_label_level_3"] = str(new_functions[5])
        df.loc[index, "manual_label"] = new_functions[6]

    return df

def separate_manual_labels(full_dataframe):
    updated_df = full_dataframe[full_dataframe["manual_label"] == False].copy()
    manual_df = full_dataframe[full_dataframe["manual_label"] == True].copy()
    if not manual_df.empty:
        manual_df.drop("manual_label", inplace = True, axis = 1)
        manual_df.to_csv("papers_to_label.csv", index=False)

    return updated_df


if (__name__ == "__main__"):

    args = get_args()
    function_map = "function_map.csv"
    converted_dataframe = prepare_csv(args.input_csv, function_map)
    final_dataframe = separate_manual_labels(converted_dataframe)
    final_dataframe.to_csv(args.output_csv, index=False)
