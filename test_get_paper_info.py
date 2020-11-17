import os
import unittest
import get_urls
import get_paper_info
import pandas as pd


class TestGetPaperInfo(unittest.TestCase):
    def setUp(self):
        df = pd.read_csv('test_papers_jq.csv')
        self.url_titles = df[['Paper title', 'URL']].values

    def test_nature(self):
        #nature article
        url = self.url_titles[1][1]
        title = self.url_titles[1][0]
        paper = get_paper_info.PaperInfoNature(url)

        #title
        self.assertEqual(paper.get_title(), title)

    def test_pubmed(self):
        #pubmed article
        url = self.url_titles[0][1]
        title = self.url_titles[0][0]
        paper = get_paper_info.PaperInfoPubMed(url)

        #title
        self.assertEqual(paper.get_title(), title)

    def test_jeb(self):
        #JEB article
        url = self.url_titles[2][1]
        title = self.url_titles[2][0]
        paper = get_paper_info.PaperInfoJEB(url)

        #title
        self.assertEqual(paper.get_title(), title)

    def test_pnas(self):
        #PNAS article
        url = self.url_titles[3][1]
        title = self.url_titles[3][0]
        paper = get_paper_info.PaperInfoPNAS(url)

        #title
        self.assertEqual(paper.get_title(), title)

    def test_springer(self):
        #Springer article
        url = self.url_titles[4][1]
        title = self.url_titles[4][0]
        paper = get_paper_info.PaperInfoSpringer(url)
        
        #title
        self.assertEqual(paper.get_title(), title)
        
if __name__ == "main":
    unittest.main()