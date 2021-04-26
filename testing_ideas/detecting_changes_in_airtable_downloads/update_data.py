# simulates overwrites to `source-data.csv`.
# the generated CSV is just meant to be a 
# placeholder for actual application that holds data 
#
# Fiels:
# id field - auto incrementing integer
# last modified - random datetime as ISO-8601
# journal title - randon number as string
# author - random number as string

import random
import datetime
from datetime import datetime, timedelta
import pathlib

seed = 42
end_date   = datetime(2020, 12, 18, 00, 00, 00)
source_csv = pathlib.Path("source-data.csv")
num_updates = 10

#TODO Number of entries should match number of lines in `source-data.csv`
num_entries=1000
ids_to_update = range(1, num_entries + 1)
ids_to_update = random.sample(ids_to_update, k=num_updates)

out_string = []

random.seed(seed)

with source_csv.open("r") as in_file:
    #Read, parse, and save first line, which is headers
    out_string.append(in_file.readline().strip())

    for line in in_file:
        id_, journal_title, author, last_modified_timestamp = line.strip().split(',')
        id_ = int(id_)
        journal_title = float(journal_title)
        author = float(author)
        last_modified_timestamp = datetime.fromisoformat(last_modified_timestamp)

        
        if id_ in ids_to_update:
            author = random.random()
            start_date = last_modified_timestamp
            last_modified_timestamp = start_date + (end_date - start_date) * random.random()

        out_string.append(f"{id_},{journal_title},{author},{last_modified_timestamp}")
        
    out_string = "\n".join(out_string)

with source_csv.open("w") as out_file:
    out_file.write(out_string)
