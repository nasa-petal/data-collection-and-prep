def convert_labels(function_map, labels):

    # separate each level of labels into its own list to make it easier to understand
    petal_level_one = function_map[0]
    petal_level_two = function_map[1]
    petal_level_three = function_map[2]
    ask_level_one = function_map[3]
    ask_level_two = function_map[4]
    ask_level_three = function_map[5]

    # Separate labels into levels
    label_level_one = labels[0]
    label_level_two = labels[1]
    label_level_three = labels[2]

    label_3_index = 0
    # PeTaL labels 0, 1, 2 | AskNature 3, 4, 5 | Manual Label Required 6
    result = [set(), set(), set(), set(), set(), set(), False]

       # Look at level 3 label to see if it exists within our function mapping

    new_labels = [[], [], [], [], [], []]
    if (label_3_index < len(label_level_three)):
        for label in label_level_three:
            index3 = ask_level_three.index(
                label) if label in ask_level_three else -1

            if (index3 > 0):
                # Check what to do based on PeTaL label
                temp_label = petal_level_three[index3]

                if temp_label == "keep":
                    new_labels[2].append(label)
                    new_labels[1].append(petal_level_two[index3])
                    new_labels[0].append(petal_level_one[index3])
                elif temp_label == "raise":
                    new_labels[1].append(petal_level_two[index3])
                    new_labels[0].append(petal_level_one[index3])
                elif temp_label == "delete":
                    pass
                elif temp_label == "manual label":
                    result[-1] = True
                else:
                    new_labels[2].append(temp_label)
                    new_labels[1].append(petal_level_two[index3])
                    new_labels[0].append(petal_level_one[index3])
            else:
                # result[2].append(label_level_three[label_index])
                pass
            # Always add ask nature labels
            new_labels[3].append(ask_level_one[index3]) if ask_level_one[index3] != "" else None
            new_labels[4].append(ask_level_two[index3]) if ask_level_two[index3] != "" else None
            new_labels[5].append(ask_level_three[index3]) if ask_level_three[index3] != "" else None
            label_3_index += 1
    result[0].update(new_labels[0])
    result[1].update(new_labels[1])
    result[2].update(new_labels[2])
    result[3].update(new_labels[3])
    result[4].update(new_labels[4])
    result[5].update(new_labels[5])

    return [list(item) for item in result[:-1]] + [result[-1]]
