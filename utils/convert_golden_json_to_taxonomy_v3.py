import json

with open("golden.json", "r") as read_file:
    papers = json.load(read_file)

def replace_label_name(paper, level, label_v2, label_v3):
    for i, label in enumerate(paper[level]):
        if label == label_v2:
            paper[level][i] = label_v3

v2_to_v3_label = {
    "process_resources": "manipulate_solids_liquids_gases_energy",
    "maintain_ecological_community": "sustain_ecological_community",
    "manage_drag/turbulence": "regulate drag/turbulence",
    "prevent_deformation": "prevent/allow_deformation",
    "manage_wear": "regulate_wear",
    "chemically_modify_or_change_energy_state": "chemically_assemble/break_down",
    "maintain_structural_integrity": "manage_mechanical_forces",
    "manage_populations/pests/diseases": "manage_populations_or_habitats",
    "physically_assemble/disassemble": "assemble/break_down_structure",
    "distribute_energy": "distribute_or_expel_energy"
}
def replace_item_in_list(l, old_item, new_item):
    for index, item in enumerate(l):
        if item == old_item:
            l[index] = new_item


def new_l2_label(paper, level3_v1, level2_v1, level2_v3):
    for i, label in enumerate(paper["level3"]):
        if label == level3_v1:
            replace_item_in_list(paper["level2"], level2_v1, level2_v3)


new_level2_label = {
    "manage_impact": ("manage_structural_forces", "manage_external_forces"),

}
# for i, label in enumerate(paper["level1"]):
    #     if label == "process_resources":
    #         paper["level1"][i] = "manipulate_solids_liquids_gases_energy"

for paper in papers:
    # print(paper)
    for level in ["level1", "level2", "level3"]:
        for v2_label in v2_to_v3_label:
            v3_label = v2_to_v3_label[v2_label]
            replace_label_name(paper, level, v2_label, v3_label)

for paper in papers:
    for level3_v1, level2_v1_and_v3 in new_level2_label.items():
        level2_v1, level2_v3 = level2_v1_and_v3
        new_l2_label(paper, level3_v1, level2_v1, level2_v3)


    # for i, label in enumerate(paper["level1"]):
    #     if label == "process_resources":
    #         paper["level1"][i] = "manipulate_solids_liquids_gases_energy"
    # print(paper)
with open("golden_v3.json", "w") as write_file:
    json.dump(papers, write_file)
