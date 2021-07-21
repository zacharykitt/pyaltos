import os
import unittest

import pendulum

from .pyaltos import AltosWrapper, date_of_last_friday


class TestPyaltos(unittest.TestCase):
    FILE_URL = 'https://www.wikipedia.org/portal/wikipedia.org/assets/img/Wikipedia-logo-v2.png'
    FILE_PATH = './test.png'
    VALID_CURRENT_DATE = '2021-06-16'
    VALID_FILE_DATE = '2021-06-11'
    VALID_FILE_ENDPOINT = 'https://data.altos.re/api/data?type=rental&amp;county=us_all-extended&amp;date='

    @classmethod
    def setUpClass(cls) -> None:
        username = os.environ['ALTOS_USERNAME']
        cls.altos = AltosWrapper(username)

    def test_date_of_last_friday(self):
        start_date = pendulum.parse(self.VALID_CURRENT_DATE)
        last_friday = date_of_last_friday(start_date)
        self.assertEqual(last_friday, self.VALID_FILE_DATE)

    def test_get_extended_file_list(self):
        files_list = self.altos.get_extended_file_list()
        self.assertGreater(len(files_list), 0)

    def test_get_latest_file_date(self):
        recent_file_date = self.altos.get_date_of_latest_file()
        self.assertEqual(recent_file_date, date_of_last_friday())

    def test_create_file_request_url_from_date(self):
        returned_url = self.altos.create_file_request_url_from_date(self.VALID_FILE_DATE)
        expected_url = self.VALID_FILE_ENDPOINT + self.VALID_FILE_DATE
        self.assertEqual(expected_url, returned_url)

    def test_create_file_request_url_from_date_with_error(self):
        with self.assertRaises(ValueError):
            returned_url = self.altos.create_file_request_url_from_date("this won't work!")

    def test_download_file_with_url(self):
        self.altos.download_file_with_url(self.FILE_URL, self.FILE_PATH, auth=False)
        self.assertTrue(os.path.isfile(self.FILE_PATH))
        os.remove(self.FILE_PATH)


if __name__ == '__main__':
    unittest.main()
