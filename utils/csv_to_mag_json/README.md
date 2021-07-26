# Convert CSV to JSON with MAG Data

## What is this script?

convert_to_mag takes in our labeled dataset in the form of a csv, looks up each paper in Microsoft Academic, merges the results and creates a JSON file from it.

## How do I run these scripts?
This script utilizes NLTK, thus before you run it, you must make sure you have NLTK installed: https://www.nltk.org/install.html. Once done you can either download all of the NLTK packages or just the ones used in this script. 

- For all files, you would run:
  - python -m nltk.downloader all
<br/><br/>
- For the files specific to this script you would run:
  - python -m nltk.downloader stopwords
  - python -m nltk.downloader punkt

This script is started with the "python" command (ex. python example_script.py). This script takes two required parameters, csv_path and output_file. The csv_path is the path of labeled datset and the output_file is simply the name that will be given to the final JSON file. This script accepts a help parameter which will repeat this information (-h, --help). <br/>

As this script utilizes the Microsoft Academic API, it also needs an API key to function. The script will look for a .env file with __MAG_KEY=\***\**__, where \***\** is the api key.