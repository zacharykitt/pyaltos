import gzip
import os
import shutil
from typing import Optional, List, Dict

import pendulum
import requests


def date_of_last_friday(start_date: Optional[pendulum.DateTime] = None) -> str:
    """
    This helper function is included because Altos releases a new file each Friday.

    :param start_date: the date from which the previous Friday should be found
    """
    if start_date is None:
        start_date = pendulum.now()
    last_friday = start_date.previous(pendulum.FRIDAY)
    return last_friday.to_date_string()


class AltosWrapper:
    extended_endpoint = 'https://data.altos.re/api/list?type=rental&amp;county=us_all-extended'
    file_endpoint = 'https://data.altos.re/api/data?type=rental&amp;county=us_all-extended&amp;date='

    def __init__(self, username: str = '', password: str = ''):
        self.username = username if username != '' else os.environ['ALTOS_USERNAME']
        self.password = password
        self.auth_tup = (self.username, self.password)

    @classmethod
    def create_file_request_url_from_date(cls, date: str):
        parsed_date = pendulum.parse(date)
        formatted_date = parsed_date.to_date_string()
        return cls.file_endpoint + formatted_date

    @staticmethod
    def deflate_downloaded_file(download_path: str) -> str:
        """
        A helper method for deflating files downloaded from Altos.

        :param download_path: the path of the downloaded file
        :return: a string with the deflated file's path
        """
        if '.gz' not in download_path:
            raise ValueError
        deflated_path = download_path.replace('.gz', '')
        with gzip.open(download_path, 'rb') as compressed_file:
            with open(deflated_path, 'wb') as deflated_file:
                shutil.copyfileobj(compressed_file, deflated_file)
        return deflated_path

    def get_extended_file_list(self) -> List[Dict]:
        """
        Queries the API for available file downloads.

        :return: a list of dictionaries
        """
        response = requests.get(self.extended_endpoint, auth=(self.username, self.password))
        response.raise_for_status()
        return response.json()

    def download_file_with_url(self, url: str, download_path: str, auth: bool = True):
        """
        Downloads a file with a given URL. Note that Altos files will be gzipped.

        :param url: the URL to download a large file from
        :param download_path: a string representing the download's filename
        :param auth: a tuple containing a username string and a password string
        """
        credentials = self.auth_tup if auth else None
        with requests.get(url, auth=credentials, stream=True) as r:
            with open(download_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

    def get_date_of_latest_file(self) -> str:
        """
        Identifies the date of the most recent file provided by the Altos API.

        :return: a string representing the most recent file's date in YYYY-MM-DD format
        """
        files_list = self.get_extended_file_list()
        most_recent_file = files_list[0]
        return most_recent_file['date']

