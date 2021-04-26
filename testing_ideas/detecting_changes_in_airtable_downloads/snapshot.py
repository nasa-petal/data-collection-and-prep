#copies data from `source-data.csv` to
#to a new csv file, to simulate taking a 
#snapshot of data from a different system
#new file is named `snapshot_<ISO-8601>`

import shutil
import datetime

timestamp = datetime.datetime.now()
timestamp = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
filename = f"snapshot_{timestamp}.csv"
shutil.copy("source-data.csv", filename)