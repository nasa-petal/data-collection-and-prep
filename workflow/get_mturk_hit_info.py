#!/usr/bin/env python
# coding: utf-8

"""
Get info about a single HIT given Id
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
parser.add_argument("hit_id", help="HITiD requested information about", type=str)
parser.add_argument("--environment", help="production or sandbox", default="sandbox", type=str,
                    choices=['production', 'sandbox'])
args = parser.parse_args()
aws_profile = args.aws_profile
environment = args.environment
hit_id = args.hit_id

client, mturk_environment = get_mturk_client(environment, aws_profile)

response = client.get_hit(
    HITId=hit_id
)

print(response)