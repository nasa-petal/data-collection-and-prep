"""
Defines the columns used in this workflow
"""
key_mapping = {
    "doi": ["DOI"],
    "url": ["Journal URL", "Primary lit site"],
    "title": ["Paper title", "Title"],
    "abstract": ["Abstract"],
    "full_doc_link":["PDF Link"],
    "is_open_access": ["Open access?"],
    "label_level_1": ["Functions Level I"],
    "label_level_2": ["Functions Level II"],
    "label_level_3": ["Functions Level III- NEW"],
    "journal":["Journal"],
}

standard_columns = list(key_mapping.keys())
