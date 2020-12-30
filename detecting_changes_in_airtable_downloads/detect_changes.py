#Compares a snapshot of data in a CSV file
#with a historical log to detect changes.
#Detected changes are written to `changed_data.csv`
#and `ops_log`. If no changes are detected, `ops_log`
#isn't updated, and `changed_data.csv` will be empty

import datetime
import pathlib

changed_data = {}
ops_log = {}
snapshots = {}
headers="id,journal_title,author,last_mod"

#only the latest changes are logged to `changed_data.csv`
#create if it doesn't exist
if not pathlib.Path("changed_data.csv").exists():
    with pathlib.Path("changed_data.csv").open("w") as out_file:
        out_file.write(headers)
        out_file.write("\n")

#history of all changes are logged to `ops_log`
#creat if it doesn't exist
if not pathlib.Path("ops_log").exists():
    with pathlib.Path("ops_log").open("w") as out_file:
        pass

#Error out if more than one snapshot exists
found_snapshots = list(pathlib.Path(".").glob("snapshot_*.csv"))

if len(found_snapshots) > 1:
    raise RuntimeError("Directory should have no more than one snapshot") 

snapshot_path = found_snapshots[0]

#read in all data from snapshot
#and convert fields to the correct data type
with pathlib.Path(snapshot_path).open("r") as in_file:
    #skip header
    in_file.readline()

    for line in in_file:
        id_, journal_title, author, last_modified_timestamp = line.strip().split(',')
        id_ = int(id_)
        journal_title = float(journal_title)
        author = float(author)
        last_modified_timestamp = datetime.datetime.fromisoformat(last_modified_timestamp)
        snapshots[id_] = (journal_title, author, last_modified_timestamp)

#read in all data from ops log
#and convert fields to the correct data type
with pathlib.Path("ops_log").open("r") as in_file:
    for line in in_file:
        id_, journal_title, author, last_modified_timestamp, rev, operation = line.strip().split(",")
        id_ = int(id_)
        journal_title = float(journal_title)
        author = float(author)
        last_modified_timestamp = datetime.datetime.fromisoformat(last_modified_timestamp)
        rev = int(rev)

        #because `id` isn't unique in the log, this will
        #will ensure only the latest revisions for an `id`
        #are kept
        ops_log[id_] = (journal_title, author, last_modified_timestamp, rev, operation)

#appends latest detected changes to `ops_log` 
#overwrites `changed_data.csv` with the latest changes
#if no changes were detected, `changed_data.csv` will be empty
#and no new information is appended to `ops_log`
with pathlib.Path("changed_data.csv").open("w") as out_file:
    with pathlib.Path("ops_log").open("a") as ops_file:
        out_string = [headers]

        #ids from the snapshot that aren't in the log
        created_ids = set(snapshots.keys()).difference(ops_log.keys())

        #ids from log that aren't in the snapshot
        #still have to compare operations to be sure that snapshot contains deletions
        maybe_deleted_ids = set(ops_log.keys()).difference(snapshots.keys())

        #ids that are both in the log and snapshot
        #still have to compare timestamps to be sure that snapshot contains updates
        maybe_updated_ids = set(snapshots.keys()).intersection(ops_log.keys())

        for id_ in created_ids:
            journal_title, author, last_modified_timestamp = snapshots[id_]

            #new rows of data are always rev 1
            rev = 1
            out_string.append(f"{id_},{journal_title},{author},{last_modified_timestamp},created")
            ops_file.write(f"{id_},{journal_title},{author},{last_modified_timestamp},{rev},created\n")

        for id_ in maybe_deleted_ids:
            journal_title, author, last_modified_timestamp, rev, operation = ops_log[id_]

            if operation != "deleted":
                rev = ops_log[id_][3] + 1 #rev number if third element in tuple
                out_string.append(f"{id_},{journal_title},{author},{last_modified_timestamp},deleted")
                ops_file.write(f"{id_},{journal_title},{author},{last_modified_timestamp},{rev},deleted\n")

        for id_ in maybe_updated_ids:
            journal_title, author, latest_modified_timestamp = snapshots[id_]
            last_modified_timestamp = ops_log[id_][2] #timestmap is second element in tuple

            if latest_modified_timestamp > last_modified_timestamp:
                rev = ops_log[id_][3] + 1 #rev number if third element in tuple
                out_string.append(f"{id_},{journal_title},{author},{latest_modified_timestamp},updated")
                ops_file.write(f"{id_},{journal_title},{author},{latest_modified_timestamp},{rev},updated\n")
    
    out_string = "\n".join(out_string)
    out_file.write(out_string)