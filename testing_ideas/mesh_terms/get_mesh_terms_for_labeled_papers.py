#!/usr/bin/env python
# coding: utf-8

import argparse
import sys
import pandas as pd
from urllib.parse import urlparse
import requests
import time

import xml.etree.ElementTree as ET

_REQUESTS_TIMEOUT = 3.0

parser = argparse.ArgumentParser(prog=sys.argv[0],
                                 description="get all the papers from the Alex and Colleen DB and find the mesh terms if possible")
parser.add_argument("papers_file", help="file containing info about the papers labeled", type=str)
parser.add_argument("output_html", help="output HTML file with paper info an mesh terms", type=str)
parser.add_argument("output_csv", help="output CSV file with paper info an mesh terms", type=str)
args = parser.parse_args()
papers_file = args.papers_file
output_html = args.output_html
output_csv = args.output_csv

df_papers_file = pd.read_csv(papers_file)

df_with_columns_of_interest = df_papers_file[['title', 'abstract', 'label_level_1', 'doi', 'url']]
df_with_columns_of_interest = df_with_columns_of_interest.fillna('')

# Uncomment if you only want 10. For debugging
# df_with_columns_of_interest = df_with_columns_of_interest.head(10)

def get_mesh_term(doi):

    # has mesh https://pubmed.ncbi.nlm.nih.gov/25483505/
    # Example
    # request
    # including
    # an
    # API
    # key:
    # esummary.fcgi?db = pubmed & id = 123456 & api_key = 6b4a04f8a642fa54bf86787c70b784a64108

    # But no MeSH terms in API results https://api.semanticscholar.org/v1/paper/PMID:25483505

    #  '10.1016/j.tibtech.2009.11.005'
    # convert doi to pubmed
    # https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=10.1093/nar/gks1195&format=json

    # returns
    #
    # {
    #     "status": "ok",
    #     "responseDate": "2021-06-02 20:42:31",
    #     "request": "tool=my_tool;email=my_email%40example.com;ids=10.1093%2Fnar%2Fgks1195;format"
    #                "=json",
    #     "records": [
    #         {
    #             "pmcid": "PMC3531190",
    #             "pmid": "23193287",
    #             "doi": "10.1093/nar/gks1195",
    #             "versions": [
    #                 {
    #                     "pmcid": "PMC3531190.1",
    #                     "current": "true"
    #                 }
    #             ]
    #         }
    #     ]
    # }


    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=23193287&api_key=6b4a04f8a642fa54bf86787c70b784a64108

    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=25483505&api_key=6b4a04f8a642fa54bf86787c70b784a64108
    # but no mesh terms

    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=pubmed&id=25483505&api_key=6b4a04f8a642fa54bf86787c70b784a64108
    # links to mesh terms?

    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=22368089&tool=my_tool&email=my_email@example.com
    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=25483505&tool=my_tool&email=my_email@example.com
    # has mesh nicely but no JSON!

    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=22368089&tool=my_tool&email=my_email@example.com&retmode=xml
    # better in XML


    # import xml.etree.ElementTree as ET

    url_components = urlparse(doi)
    path = url_components.path  # e.g. '/article/10.1007%2Fs002270000466'
    ss_api_url = f'https://api.semanticscholar.org/v1/paper/{path}'
    response = requests.get(ss_api_url, timeout=_REQUESTS_TIMEOUT)
    if response.ok:
        ss_api_query_results = response.json()
        q = ss_api_query_results
    else:
        ss_api_query_results = None

def get_mesh_terms_from_pmid(pmid):
    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=22368089&tool=my_tool&email=my_email@example.com&retmode=xml
    import time
    time.sleep(0.4)
    # print("get_mesh_term_from_pmid")
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&tool=my_tool&email=hschilling@nasa.gov&retmode=xml"
    response = requests.get(url, timeout=_REQUESTS_TIMEOUT)
    # query_results = response.json()

    mesh_terms = []
    try:
        root = ET.fromstring(response.text)

        for mesh_heading in root.iter('MeshHeading'):
            mesh_term_parts = []
            for child in mesh_heading:
                mesh_term_parts.append(child.text)
            mesh_terms.append(" / ".join(mesh_term_parts))
    except Exception as err:
        print(f"Error while getting mesh terms from {pmid}")
        print(str(err))
    return mesh_terms


def doi_to_pmid_using_ncbi(doi):
    time.sleep(0.4)
    # print("doi_to_pmid_using_ncbi")
    url_components = urlparse(doi)
    path = url_components.path  # e.g. '/article/10.1007%2Fs002270000466'
    path = path[1:]
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=hschilling@nasa.gov&ids={path}&format=json"
    response = requests.get(url, timeout=_REQUESTS_TIMEOUT)
    query_results = response.json()
    pmid = ''
    if query_results['status'] == 'ok':
        if 'pmid' in query_results['records'][0] :
            pmid = query_results['records'][0]['pmid']
    return pmid

def doi_to_pmid_using_ss(doi):
    time.sleep(0.4)
    # print("doi_to_pmid_using_ss")
    url_components = urlparse(doi)
    path = url_components.path  # e.g. '/article/10.1007%2Fs002270000466'
    ss_api_url = f'https://api.semanticscholar.org/v1/paper{path}'
    response = requests.get(ss_api_url, timeout=_REQUESTS_TIMEOUT)
    if response.ok:
        ss_api_query_results = response.json()
    else:
        ss_api_query_results = None
    print(ss_api_query_results)

def get_mesh_terms_2(doi):
    # print("get_mesh_term_2")
    if not doi.startswith("https"): # for some reason some are missing the first part
        doi = "https://doi.org/" + doi
    pmid_from_ncbi = doi_to_pmid_using_ncbi(doi)
    # pmid_from_ss = doi_to_pmid_using_ss(doi)
    if pmid_from_ncbi:
        mesh_terms = get_mesh_terms_from_pmid(pmid_from_ncbi)
    else:
        mesh_terms = []
    # print(doi, pmid_from_ncbi, pmid_from_ncbi, mesh_terms)
    print(doi, pmid_from_ncbi, mesh_terms)
    return pmid_from_ncbi, mesh_terms

# def get_mesh_terms_3(doi): # use SS API
#     import time
#     time.sleep(0.4)
#     print("get_mesh_term_3")
#     url_components = urlparse(doi)
#     path = url_components.path  # e.g. '/article/10.1007%2Fs002270000466'
#     ss_api_url = f'https://api.semanticscholar.org/v1/paper{path}'
#     response = requests.get(ss_api_url)
#     if response.ok:
#         ss_api_query_results = response.json()
#     else:
#         ss_api_query_results = None
#     pmid = ''
#     mesh_terms = []
#     if query_results['status'] == 'ok':
#         if 'pmid' in query_results['records'][0] :
#             pmid = query_results['records'][0]['pmid']
#             mesh_terms = get_mesh_terms_from_pmid(pmid)
#     print(doi, pmid, mesh_terms)
#     return mesh_terms

df_output = pd.DataFrame(columns=['title', 'abstract', 'label_level_1', 'doi', 'url', 'mesh_term'])


mesh_terms = []
num_papers = 0
num_doi = 0
num_pmid = 0
num_mesh_terms = 0
for index, row in df_with_columns_of_interest.iterrows():
    num_papers += 1
    # if index > 10:
    #     break
    title, abstract, label_level_1, doi, url = row
    print(f"\n\n**** Getting mesh terms for {doi} ***")

    if doi:
        pmid, terms = get_mesh_terms_2(doi)


    if terms:
        for term in terms:
            df_output = df_output.append(
                {'title': title,
                 'abstract': abstract,
                 'label_level_1': label_level_1,
                 'doi': doi,
                 'url': url,
                 'mesh_term': term,
                 },
                ignore_index=True)
    else:
        df_output = df_output.append(
            {'title': title,
             'abstract': abstract,
             'label_level_1': label_level_1,
             'doi': doi,
             'url': url,
             'mesh_term': '',
             },
            ignore_index=True)

    mesh_terms.append(terms)

    if doi:
        num_doi += 1
    if pmid:
        num_pmid += 1
    if terms:
        num_mesh_terms += 1

print(f"num_papers: {num_papers} num_doi: {num_doi} num_pmid:{num_pmid} num_mesh_terms:{num_mesh_terms}" )
# df_with_columns_of_interest["Mesh Terms"] = mesh_terms







# df_with_columns_of_interest.to_html(output_html)
# df_with_columns_of_interest.to_csv(output_csv)


df_output.to_html(output_html)


df_output.to_csv(output_csv)