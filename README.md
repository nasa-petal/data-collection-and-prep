# Overview

This directory contains scripts, notebooks, data, and docs used for collecting data about papers
so that a machine learning model can be created to label papers with biomimicry functions.

The most important folder is the `workflow` folder.

## Directory descriptions

Here are some brief explanations of what the folders contain.

- **data**  
Contains a variety of data files generated as a result of running the scripts. It includes the "primary CSV database".
- **docs**  
Legacy files. Not used currently
- **downloaders**  
Code to do downloading of information from journal paper sites. Code not used at the moment
- **notebooks**  
Some Jupyter notebooks used for exploring doing some data collection and transformations
- **testing_ideas**  
A collection of folders with scripts written to test out ideas for code that can be used for the data
 collection workflow
- **tests**  
Test code. Not maintained. Many more tests need to be written
- **utils**  
A collection of scripts that can be used for small tasks
- **workflow**  
The most important code in this repo lives in this folder. There are many scripts used to generate the data
for the machine learning training and also some scripts to generate reports about the process. See the 
README file in the directory for more information

