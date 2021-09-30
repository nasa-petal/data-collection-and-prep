#!/usr/bin/env python
# coding: utf-8

"""
Get the results from workers doing our HITs
"""

import sys
import argparse
import json
from datetime import datetime
import pytz

from workflow_utilities import get_mturk_client

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

def get_all_assignments(client, hit_id):
    initial = True
    all_assignments = []
    while initial or ('NextToken' in all_assignments_info):
        if initial:
            all_assignments_info = client.list_assignments_for_hit(HITId=hit_id, MaxResults=100)
        else:
            all_assignments_info = client.list_assignments_for_hit(HITId=hit_id, MaxResults=100,
                                                    NextToken=all_assignments_info['NextToken'])
        all_assignments.extend(all_assignments_info['Assignments'])
        initial = False

    return all_assignments


parser = argparse.ArgumentParser(prog=sys.argv[0],
                                 description="get a dump of all the HIT information from MTurk.")
parser.add_argument("aws_profile", help="AWS Profile Name", type=str)
parser.add_argument("--environment", help="production or sandbox", default="sandbox", type=str,
                    choices=['production', 'sandbox'])
args = parser.parse_args()
aws_profile = args.aws_profile
environment = args.environment

client, mturk_environment = get_mturk_client(environment, aws_profile)

date_and_time = datetime.now(tz=pytz.utc).strftime('%Y-%m-%d_%H-%M-%S-%Z.json')
outfile = f"mturk_dump_from_{environment}_{date_and_time}"

hits = get_all_hits(client)

results = []
with open(outfile, "w") as f:
    for hit in hits:
        assignments = get_all_assignments(client, hit['HITId'])
        hit['assignments'] = assignments
        results.append(hit)
    f.write(json.dumps(results, indent=2, sort_keys=True, default=str))


