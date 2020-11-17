import os
import unittest

import get_urls


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
        second_url = urls[1]
        third_url = urls[2]
        self.assertEqual('https://pubmed.ncbi.nlm.nih.gov/19113150/', first_url)
        self.assertEqual('https://science.sciencemag.org/content/315/5810/348', second_url)
        self.assertEqual('https://zslpublications.onlinelibrary.wiley.com/doi/abs/10.1111/j.1469-7998.1973.tb04553.x', third_url)

unittest.main()