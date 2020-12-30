#generates data and writes it to `source-data.csv`.
# the generated CSV is just meant to be a 
# placeholder for actual application that holds data 
#
# Fiels:
# id field - auto incrementing integer
# last modified - random datetime as ISO-8601
# journal title - randon number as string
# author - random number as string

import random
from datetime import datetime, timedelta
import pathlib

start_date = datetime(2020, 1, 1, 00, 00, 00)
end_date   = datetime(2020, 9, 1, 00, 00, 00)

seed = 42
source_csv = pathlib.Path("source-data.csv")
num_entries = 1000
ids_ = range(1, num_entries + 1)
headers="id,journal_title,author,last_mod"

random.seed(seed)

with source_csv.open("w") as out_file:
    out_string = [headers]

    for id_ in ids_:
        #Generate random datetime 
        last_modified_timestamp= start_date + (end_date - start_date) * random.random()
        author = random.random()
        journal_title = random.random()

        out_string.append(f"{id_},{journal_title},{author},{last_modified_timestamp}")

    out_string = "\n".join(out_string)
    out_file.write(out_string)
