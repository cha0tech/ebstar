from dataclasses import dataclass
from datetime import datetime
import os.path
import requests
import time

from datatypes import Route


class ApiClient:
    def __init__(self, headers_file, cookie_file):
        self._cookie_file = cookie_file
        self._read_headers(headers_file)
        self._read_cookie()
        self._session = requests.Session()

    def _read_headers(self, headers_file):
        self._headers = {}
        with open(headers_file) as headers_in:
            self._headers = dict(line.strip().split(': ', 1)
                                 for line in headers_in)

    def _read_cookie(self):
        with open(self._cookie_file) as cookie_in:
            self._cookie_file_mtime = os.path.getmtime(self._cookie_file)
            self._headers['Cookie'] = cookie_in.read().strip()

    def check_status(self):
        req = self._session.get('https://api.my-ip.io/ip')
        print('IP address:', req.text)
        print('Sending sample request ... ', end='')
        res = self.send_request(Route('ARN', 'MUC', '20221112'))
        if not res.is_valid:
            raise ValueError(
                f'Failed sample request (status_code={res.response.status_code}, cookie_expired={res.is_cookie_expired})')
        print('success')

    def send_request(self, route):
        url = f'https://www.sas.se/api/offers/flights?to={route.iata_to}&from={route.iata_from}&outDate={route.date}&adt=1&chd=0&inf=0&yth=0&bookingFlow=star&pos=se&channel=web&displayType=upsell'
        res = self._session.get(url, headers=self._headers, timeout=30)
        return ApiResponse(route, res, datetime.now())

    def wait_for_new_cookie(self):
        print('Waiting for new cookie file ... ', end='')
        while not self._is_cookie_file_modified() or self._is_cookie_file_empty():
            time.sleep(1)
        self._read_cookie()
        print('updated.')

    def _is_cookie_file_modified(self):
        return os.path.getmtime(self._cookie_file) != self._cookie_file_mtime

    def _is_cookie_file_empty(self):
        with open(self._cookie_file) as cookie_in:
            return len(cookie_in.read()) == 0


@dataclass(frozen=True)
class ApiResponse:
    route: Route
    response: requests.Response
    timestamp: datetime

    @property
    def application_errors(self):
        json = self.response.json()
        if 'errors' not in json:
            return {}
        return {int(entry['errorCode']): entry['errorMessage'] for entry in json['errors']}

    @property
    def is_cookie_expired(self):
        return self.response.status_code == 403 and 'Pardon Our Interruption' in self.response.text

    @property
    def is_valid(self):
        return self.response.status_code == 200 and 225064 not in self.application_errors.keys()
