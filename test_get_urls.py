import os
import unittest

import get_urls

# urls = get_urls.get_urls("test_papers.csv")
# print(urls)

class TestGetUrls(unittest.TestCase):
    def setUp(self):
        pass # Nothing for now

    def tearDown(self):
        pass # Nothing for now

    def test_get_urls(self):
        # Need to put a "test" CSV file in this directory
        # Let's say it is called "test_papers.csv", has 3 papers in it, and the first
        #  is a URL of "https://pubmed.ncbi.nlm.nih.gov/19113150/"
        # To test the get_urls function

        urls = get_urls.get_urls("test_papers.csv")

        self.assertEqual(3, len(urls))

        first_url = urls[0]
        self.assertEqual('https://pubmed.ncbi.nlm.nih.gov/19113150/', first_url)

unittest.main()