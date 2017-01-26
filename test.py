import json
import unittest
import pandas as pd
from pprint import pprint
from app import app


class APITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        """
        fetch the list of ids and sample a random client_id

        use that id to test the route, also query Socrata directy to compare values
        """
        #TODO these tests are really slow, lots of redundant data queries
        self.client = app.test_client(self)
        list_url = 'https://data.pa.gov/resource/vsaj-gjez.json?$select=client_id'
        raw_client_list = pd.read_json(list_url)
        self.choice = raw_client_list.sample().values[0]
        response_url = 'https://data.pa.gov/resource/vsaj-gjez.json?client_id=%d&$limit=1' % self.choice
        self.df_init = pd.read_json(response_url, dtype=False)
        count_url = 'https://data.pa.gov/resource/vsaj-gjez.json?$select=count(*),max(client_id)&client_id=%d' % self.choice
        self.count = pd.read_json(count_url)
        self.response = self.client.get('/client_id/%d' % self.choice)
        print("Fetched client_id is: " , self.choice )

    def test_query(self):
        self.assertEqual(self.response.status_code, 200)
        pprint(json.loads(self.response.get_data()))
    def test_client_id_match(self):
        self.assertEqual(json.loads(self.response.data)['client_id'], self.df_init['client_id'][0])
    def test_client_count_match(self):
        self.assertEqual(json.loads(self.response.data)['count'], self.count['count_1'][0])

if __name__ == '__main__':
    unittest.main()
