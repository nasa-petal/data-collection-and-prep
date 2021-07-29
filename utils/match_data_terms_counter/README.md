# Lens Counter

This script exists to count the count the occurences of MAG and MeSH terms in the data which we feed into our model. The script accepts a JSON newline delimted file where each JSON object contains the parameters of "mesh" and "mag", each containing a list of their respective terms.

## How do I run it?

The script can be run by calling it with python (python *file_name.py*) and passing in the full or relative path of the JSON newline delimited file as an argument.

## Results 07-21-2021

As we can see below, 961 out of the 1000 papers MATCH is currently using, have associated MAG terms, while only 571 have associated MeSH terms.

```
MeSH Terms Only: 11
MAG Terms Only: 401
Both: 560
None: 28
```