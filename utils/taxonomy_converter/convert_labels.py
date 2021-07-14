def convert_labels(function_map, labels):

    # separate each level of labels into its own list to make it easier to understand
    level_one = function_map[0]
    level_two = function_map[1]
    level_three = function_map[2]

    # Separate labels into levels
    label_level_one = labels[0]
    label_level_two = labels[1]
    label_level_three = labels[2]

    label_1_index = 0
    label_2_index = 0
    label_3_index = 0

    result = [[], [], []]

    for label_index in range(max([len(label_level_one), len(label_level_two), len(label_level_three)])):

        if (label_1_index < len(label_level_one)):
            index1 = level_one.index(
                label_level_one[label_index]) if label_level_one[label_index] in level_one else -1
            if (index1 > 0):
                result[0].append(level_one[index1])
            else:
                # result[0].append(label_level_one[label_index])
                print(label_level_one[label_index])
                pass
            label_1_index += 1

        if (label_2_index < len(label_level_two)):
            index2 = level_two.index(
                label_level_two[label_index]) if label_level_two[label_index] in level_two else -1
            if (index2 > 0):
                result[1].append(level_two[index2])
            else:
                # result[1].append(label_level_two[label_index])
                pass
            label_2_index += 1

        if (label_3_index < len(label_level_three)):
            index3 = level_three.index(
                label_level_three[label_index]) if label_level_three[label_index] in level_three else -1
            if (index3 > 0):
                result[2].append(level_three[index3])
            else:
                # result[2].append(label_level_three[label_index])
                pass
            label_3_index += 1

    return result
