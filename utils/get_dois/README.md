# Extract DOIs

## What are these scripts?

### Summary
Both of these scripts take the URL of a digital publication and return the DOI of it.

### get_doi
The __get_doi__ script takes a single URL and returns a single DOI.

### get_dois
The __get_dois__ script ingests a text file of URLS separated by newline characters and returns:
<ul>
<li>A text file containing dois or "error" texts separated by newline characters.</li>
<li>An error log containing a date stamp, the faulty URL and the type of error thrown.</li>
</ul>

The new_dois file will be in the same order as the urls were in, within the text file. Meaning, if the information was copied from a csv file through a program like Excel or Google Sheets. The information can be directly copied and pasted back into the csv file.

## How do I run these scripts?
Both scripts are run by starting them with the "python" command (ex. python example_script.py). Both scripts accept a help parameter which will repeat the below information (-h, --help).

### get_doi
<p>The __get_doi__ script requires a single argument (url) which is the URL of the digital publication.</p>

### get_dois
<p>The __get_dois__ script accepts two arguments, the first being "-p, --path", which is the path + file_name and extension of the text file containing URLs. The second argument is "-o, --overwrite", which dictates whether or not to overwrite the error_logs file if it already exists.</p>