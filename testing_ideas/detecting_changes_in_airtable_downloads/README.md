# Scripts to detect changes in download of CSV files from AirTable
We want to intelligently handle changes to the files we download from AirTable so we don't re-do work in the pipeline.

- gen_data.py
   - generates data and writes it to `source-data.csv`. The generated CSV is just meant to be a 
placeholder for actual application that holds data
- snapshot.py
   - copies data from `source-data.csv` to to a new csv file, to simulate taking a snapshot of data from a different system
- update_data.py
   - simulates overwrites to `source-data.csv`. The generated CSV is just meant to be a placeholder for actual application that holds data
- detect_changes.py
   - Compares a snapshot of data in a CSV file with a historical log to detect changes. Detected changes are written to `changed_data.csv`
 and `ops_log`. If no changes are detected, `ops_log` #isn't updated, and `changed_data.csv` will be empty

#### Example

```
python gen_data.py
python snapshot.py
python detect_changes.py
python update_data.py
python snapshot.py
rm snapshot_2020-12-30_15-49-24.csv # just an example. Need to remove all snapshots except the last one
python detect_changes.py
# Look at ops_log file to see log of records created and updated
```

Code written by Calvin Robinson