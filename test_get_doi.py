import unittest
import get_doi
import get_urls


class TestGetDOI(unittest.TestCase):
    def setUp(self):
        self.urls = get_urls.get_urls("test_papers_jq.csv")


    def test_get_doi_from_href(self):
        url = self.urls[0]
        doi = get_doi.pull_doi(url)

        self.assertEqual(doi, '10.1103/physreve.78.051902')

    def test_get_doi_from_text(self):
        url = self.urls[3]
        doi = get_doi.pull_doi(url)

        self.assertEqual(doi, '10.1073/pnas.0604972103')


if __name__ == "__main__":
    unittest.main()
