#!/usr/bin/env python
# coding: utf-8

"""
Get the results from workers doing our HITs
"""

import sys
import argparse
import csv

import boto3
import xmltodict
import pandas as pd

from workflow_utilities import get_mturk_client

parser = argparse.ArgumentParser(prog=sys.argv[0],
                                 description="get results from a list of HITs.")
parser.add_argument("aws_profile", help="AWS Profile Name", type=str)
parser.add_argument("--environment", help="production or sandbox", default="sandbox", type=str,
                    choices=['production', 'sandbox'])
args = parser.parse_args()
aws_profile = args.aws_profile
environment = args.environment

client, mturk_environment = get_mturk_client(environment, aws_profile)

# response = client.get_account_balance()
# print(response)

# print(mturk_environment)

def get_all_hits(client):
    initial = True
    all_hits = []
    while initial or ('NextToken' in all_hits_info):
        if initial:
            all_hits_info = client.list_hits(MaxResults=100)
        else:
            all_hits_info = client.list_hits(MaxResults=100, NextToken=all_hits_info['NextToken'])
        all_hits.extend(all_hits_info['HITs'])
        initial = False

    return all_hits

hits = get_all_hits(client)

for hit in hits:
    response = client.get_hit(
        HITId=hit['HITId']
    )
    response = client.list_assignments_for_hit(
        HITId=hit['HITId'],
        MaxResults=3,
        # AssignmentStatuses=[
        #     'Submitted' | 'Approved' | 'Rejected',
        # ]
    )
    for assignment in response['Assignments']:
        response = client.get_assignment( AssignmentId = assignment['AssignmentId'])
        print(response['Assignment']['Answer'])

        # What we can get:
        #    category.labels
        #    phrase
        #    user_labels
        #    HITId
        #    HITTypeId
        #    HITGroupId
        #    Reviewable
        #    MaxAssignments
        #    Reward
# print(hits)