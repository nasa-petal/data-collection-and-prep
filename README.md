# crowdsourcing_papers
Starting with a list of URLs of papers that can be used for crowdsourcing, create a CSV file with the URL, DOI of the paper, Title, Abstract, and if the paper is open access.

Outline
- Export CSV from Airtable
- Extract URLs from CSV
- Get HTML of the Webpage at the URL
- Extract from the HTML ( the code for each these depends on which journal or source )
  - Title
  - DOI
  - Abstract
  - Link to the full document
  - Check to see if the full document is open access
- Put all of this info for each paper into a new CSV that will be used for MTurk
