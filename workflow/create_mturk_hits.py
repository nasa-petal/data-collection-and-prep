#!/usr/bin/env python
# coding: utf-8

"""
Given a CSV file with information about a paper, generate HITs on
MTurk using their API.
"""

import boto3
import csv
import argparse
import sys

from workflow_utilities import get_mturk_client

parser = argparse.ArgumentParser(prog=sys.argv[0],
                                 description="generate MTurk HITs from a CSV file.")
parser.add_argument("aws_profile", help="AWS Profile Name", type=str)
parser.add_argument("papers_csv", help="CSV file with title, abstract, and URL for papers",
                    type=str)
parser.add_argument("hits_ids_file", help="file containing HIT IDs generated", type=str)
parser.add_argument("--max_assignments", help="Maximum MTurk Assignments", default=1, type=int)
parser.add_argument("--max_hits", help="Maximum HITS created", default=4, type=int)
parser.add_argument("--lifetime_in_days", help="How many days will the HITs be available",
                    default=30, type=int)
parser.add_argument("--assignment_duration_in_minutes",
                    help="How many minutes does the worker have to complete the HITS",
                    default=20, type=int)
parser.add_argument("--environment", help="production or sandbox", default="sandbox", type=str,
                    choices=['production', 'sandbox'])
args = parser.parse_args()
aws_profile = args.aws_profile
papers_csv = args.papers_csv
hits_ids_file = args.hits_ids_file
max_assignments = args.max_assignments
max_hits = args.max_hits
lifetime_in_days = args.lifetime_in_days
assignment_duration_in_minutes = args.assignment_duration_in_minutes
environment = args.environment

# Create the MTurk client object used to interact with MTurk
client, mturk_environment = get_mturk_client(environment, aws_profile)

# The file mturk_template.html has the template for the HITs
html_layout = open('./mturk_template.html', 'r').read()
QUESTION_XML = """<HTMLQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd">
        <HTMLContent><![CDATA[{}]]></HTMLContent>
        <FrameHeight>650</FrameHeight>
        </HTMLQuestion>"""
question_xml = QUESTION_XML.format(html_layout)

TaskAttributes = {
    'MaxAssignments': max_assignments,
    # How long the task will be available on MTurk (10 days)
    'LifetimeInSeconds': lifetime_in_days*24*60*60,
    # How long Workers have to complete each item (20 minutes)
    'AssignmentDurationInSeconds': 60*assignment_duration_in_minutes,
    # The reward you will offer Workers for each response
    'Reward': '0.00',                     
    'Title': 'Petal labeling',
    'Keywords': 'biomimicry',
    'Description': 'Label the paper.'
}

# Loop over the papers in the CSV file
results = []
hit_type_id = ''

with open(hits_ids_file, 'w') as hitsfile:
    writer = csv.writer(hitsfile)
    with open(papers_csv, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader) # skip the header
        count = 0
        for i, row in enumerate(reader):
            if count >= max_hits: break
            id,title,doi,abstract,labels,url,literature_site,full_doc_link,is_open_access,use = row
            response = client.create_hit(
                **TaskAttributes,
                Question=question_xml.replace('${title}',title).replace('${abstract}',abstract).replace('${url}',url)
            )
            hit_type_id = response['HIT']['HITTypeId']
            hit_id = response['HIT']['HITId']
            results.append({
                'title': title,
                'abstract': abstract,
                'url': url,
                'hit_id': hit_id,
            })
            writer.writerow((hit_id,url))
            count += 1

# Print out the URL to where you can view the HITs
print("You can view the HITs here:")
print(mturk_environment['preview']+"?groupId={}".format(hit_type_id))


