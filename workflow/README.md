# Data Collection Workflow Files

This folder contains the code used to collect data via Web scraping, APIs, and MTurk. This data is used to 
train the machine learning model. 

## Code file descriptions

First Term
: This is the definition of the first term.

Second Term
: This is one definition of the second term.
: This is another definition of the second term.

- **column_definitions.py**  
Contains the list of columns/fields in our resulting CSV "database"
- **create_mturk_hits.py**  
Second item having index value 2, beside we gave it 1, which indicates that markdown parser does not break the list.
- **generate_ml_training_data.py**  
Takes the contents of the primary CSV database file and does some processing to make it ready for ML model
training.
- **generate_paper_info_summary.py**  
Look through the primary CSV database and generate a summary that lets us know 
where we stand on the data collection efforts
- **generate_status_summary.py**  
While the `scrape_paper_info.py` script runs, it generates a status file for each attempted scraping. This 
script goes through that status file and generates a summary of the scraping run
- **get_hits_results.py**  
Use the MTurk API to get the results of our HITs and generate a CSV file with the results. It also creates 
an HTML file for easy viewing.
- **get_paper_info.py**  
A collection of classes used in the scraping script. Each class has code for scraping a specific site
containing papers.
- **mturk_template.html**  
The MTurk HTML template file that is used for the HITs collecting labels for papers
- **retrieve_airtable.py**  
Given the name of a table in Alex's Airtable, return the contents and place it in a CSV file.
- **scrape_paper_info.py**  
This is the script that scrapes Web sites and used APIs to get information about a paper.
- **update_paper_info_db.py**  
This script just goes through the existing primary CSV database file and tries to fill in any blanks 
in records. It differs from `scrape_paper_info.py` in that no new URLs to paper pages is given.
- **update_papers_labeled_with_hits_results.py**  
Use the labels from the HITs to update the primary CSV database
- **workflow_utilities.py**  
Some helper functions used by multiple scripts
