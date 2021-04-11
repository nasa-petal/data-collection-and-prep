#!/usr/bin/env python
# coding: utf-8

import boto3
import csv
import xmltodict
import json
import pprint

# Create the MTurk client object used to interact with MTurk
create_hits_in_production = False # Change this to True if publishing to production, not sandbox
environments = {
  "production": {
    "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
    "preview": "https://www.mturk.com/mturk/preview"
  },
  "sandbox": {
    "endpoint": 
          "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
    "preview": "https://workersandbox.mturk.com/mturk/preview"
  },
}
mturk_environment = environments["production"] if create_hits_in_production else environments["sandbox"]
session = boto3.Session(profile_name='mturk_sandbox')  # This profile was created using AWS command line tools. Creating the that involved using access keys
client = session.client(
    service_name='mturk',
    region_name='us-east-1',
    endpoint_url=mturk_environment['endpoint'],
)

# The sandbox always has an account balance of $10,000
print(client.get_account_balance()['AvailableBalance'])

# The file mturk_template.html has the template for the HITs
html_layout = open('./mturk_template.html', 'r').read()
QUESTION_XML = """<HTMLQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd">
        <HTMLContent><![CDATA[{}]]></HTMLContent>
        <FrameHeight>650</FrameHeight>
        </HTMLQuestion>"""
question_xml = QUESTION_XML.format(html_layout)

# MaxAssignments set to 1 here because I wanted to test this and so this way I could be the
# #    one and only worker working on this and it would be done
TaskAttributes = {
    'MaxAssignments': 1,           
    # How long the task will be available on MTurk (1 hour)     
    'LifetimeInSeconds': 60*60,
    # How long Workers have to complete each item (10 minutes)
    'AssignmentDurationInSeconds': 60*10,
    # The reward you will offer Workers for each response
    'Reward': '0.00',                     
    'Title': 'Petal labeling',
    'Keywords': 'biomimicry',
    'Description': 'Label the paper.'
}

# Loop over the papers
# Read the CSV file from the ground truth AirTable. The path to this needs to be adjusted as needed
results = []
hit_type_id = ''
with open('ground_truth.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader) # skip the header
    for i, row in enumerate(reader):
        title, abstract, url = row
        response = client.create_hit(
            **TaskAttributes,
            Question=question_xml.replace('${title}',title).replace('${abstract}',abstract).replace('${url}',url)
        )
        hit_type_id = response['HIT']['HITTypeId']
        results.append({
            'title': title,
            'abstract': abstract,
            'url': url,
            'hit_id': response['HIT']['HITId']
        })
        if i > 0: break   # Only want to do a couple HITs for now

# Print out the URL to where you can view the HITs
print("You can view the HITs here:")
print(mturk_environment['preview']+"?groupId={}".format(hit_type_id))

# At this point, go into MTurk as a worker, and Accepted and Work the HITs
# Get the results of assigning values as part of the HITs
questions_and_answers = []
for item in results:
    result = {
        'question': item,
        'answers': []
    }
    # Get the status of the HIT
    hit = client.get_hit(HITId=item['hit_id'])
    item['status'] = hit['HIT']['HITStatus']
    result['question']['status'] = hit['HIT']['HITStatus']
    # Get a list of the Assignments that have been submitted
    assignmentsList = client.list_assignments_for_hit(
        HITId=item['hit_id'],
        AssignmentStatuses=['Submitted', 'Approved'],
        # MaxResults=10
    )
    assignments = assignmentsList['Assignments']
    for assignment in assignments:
        # Retreive the attributes for each Assignment
        worker_id = assignment['WorkerId']
        assignment_id = assignment['AssignmentId']

        answer_dict = {
            'worker_id': worker_id,
            'assignment_id': assignment_id,
            'category.labels': '',
            'phrase': '',
            'user_labels': '',
            'ranking': '',
        }

        answer_fields_from_mturk = xmltodict.parse(assignment['Answer'])['QuestionFormAnswers']['Answer']
        for field in answer_fields_from_mturk:
            question_id = field['QuestionIdentifier']
            answer_text = field['FreeText']
            answer_dict[question_id] = answer_text

        result['answers'].append(answer_dict)

    questions_and_answers.append(result)


print(json.dumps(questions_and_answers,indent=2))

# This code just shows how to get at the results and prints them out as we learn
# for item in results:
#
#     pprint.pprint(item)
#
#     # Get the status of the HIT
#     hit = client.get_hit(HITId=item['hit_id'])
#     item['status'] = hit['HIT']['HITStatus']
#     # Get a list of the Assignments that have been submitted
#     assignmentsList = client.list_assignments_for_hit(
#         HITId=item['hit_id'],
#         AssignmentStatuses=['Submitted', 'Approved'],
#         MaxResults=10
#     )
#     assignments = assignmentsList['Assignments']
#     item['assignments_submitted_count'] = len(assignments)
#     answers = []
#     print(len(assignments))
#     for assignment in assignments:
#
#         # Retreive the attributes for each Assignment
#         worker_id = assignment['WorkerId']
#         assignment_id = assignment['AssignmentId']
#
#         print('***')
#
#         pprint.pprint(assignment)
#
#         print('***')
#
#         # Retrieve the value submitted by the Worker from the XML
#         answer_dict = xmltodict.parse(assignment['Answer'])
#         pprint.pprint(answer_dict.keys())
#         pprint.pprint(answer_dict['QuestionFormAnswers'].keys())
#         pprint.pprint(answer_dict['QuestionFormAnswers']['@xmlns'])
#         print()
#         print()
#         pprint.pprint(answer_dict['QuestionFormAnswers']['Answer'][0].keys())
#         print()
# #         pprint.pprint(answer_dict['QuestionFormAnswers']['Answer'][3]['FreeText'])
#         print()
#         labels = answer_dict['QuestionFormAnswers']['Answer'][0]['FreeText']
#         their_labels = answer_dict['QuestionFormAnswers']['Answer'][1]['FreeText']
#         their_phrase = answer_dict['QuestionFormAnswers']['Answer'][2]['FreeText']
#         their_ranking = answer_dict['QuestionFormAnswers']['Answer'][3]['FreeText']
#
#         print(labels)
#         print(their_labels)
#         print(their_phrase)
#         print(their_ranking)
#         print(f"worker id: {assignment['WorkerId']}")
#         print('-----')
#
#
# # Learning how to get at all the assignments in the HITs
# for item in results:
#
#     # Get the status of the HIT
#     hit = client.get_hit(HITId=item['hit_id'])
#     item['status'] = hit['HIT']['HITStatus']
#     # Get a list of the Assignments that have been submitted
#     assignmentsList = client.list_assignments_for_hit(
#         HITId=item['hit_id'],
#         AssignmentStatuses=['Submitted', 'Approved'],
#         MaxResults=10
#     )
#     assignments = assignmentsList['Assignments']
#     item['assignments_submitted_count'] = len(assignments)
#     answers = []
#     for assignment in assignments:
#
#         # Retreive the attributes for each Assignment
#         worker_id = assignment['WorkerId']
#         assignment_id = assignment['AssignmentId']
#
#         # Retrieve the value submitted by the Worker from the XML
#         answer_dict = xmltodict.parse(assignment['Answer'])
#         print( "Worker's answer was:")
#         for answer_field in answer_dict['QuestionFormAnswers']['Answer']:
#             print( "For input field: " + answer_field['QuestionIdentifier'])
#             print( "Submitted answer: " + answer_field['FreeText'])
#
# # Experimenting with looking at all hits
# response = client.list_hits(MaxResults=100)
# hits = response['HITs']
# for hit in hits:
#     print(hit['HITId'],hit['HITTypeId'],hit['HITGroupId'],hit['Title'],hit['HITStatus'])
#     print()
#     assignments_response = client.list_assignments_for_hit(HITId=hit['HITId'])
#     assignments = assignments_response['Assignments']
#     for assignment in assignments:
#         print('     ', assignment['WorkerId'], ['AssignmentStatus'])


# This is the code from the example

# for item in results:
#
#     # Get the status of the HIT
#     hit = client.get_hit(HITId=item['hit_id'])
#     item['status'] = hit['HIT']['HITStatus']
#     # Get a list of the Assignments that have been submitted
#     assignmentsList = client.list_assignments_for_hit(
#         HITId=item['hit_id'],
#         AssignmentStatuses=['Submitted', 'Approved'],
#         MaxResults=10
#     )
#     assignments = assignmentsList['Assignments']
#     item['assignments_submitted_count'] = len(assignments)
#     answers = []
#     for assignment in assignments:
#
#         # Retreive the attributes for each Assignment
#         worker_id = assignment['WorkerId']
#         assignment_id = assignment['AssignmentId']
#
#         # Retrieve the value submitted by the Worker from the XML
#         answer_dict = xmltodict.parse(assignment['Answer'])
#         answer = answer_dict['QuestionFormAnswers']['Answer']['FreeText']
#         answers.append(int(answer))
#
#         # Approve the Assignment (if it hasn't been already)
#         if assignment['AssignmentStatus'] == 'Submitted':
#             client.approve_assignment(
#                 AssignmentId=assignment_id,
#                 OverrideRejection=False
#             )
#
#     # Add the answers that have been retrieved for this item
#     item['answers'] = answers
#     if len(answers) > 0:
#         item['avg_answer'] = sum(answers)/len(answers)
# print(json.dumps(results,indent=2))





