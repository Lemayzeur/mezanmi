from django.conf import settings
from django.utils import timezone

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy

import datetime
import requests
import pickle
import time

class ExchangeRateBackend:
    def __init__(self):
        self._response = {}

    def _get_fake_headers(self):
        # Use a fake user agent to simulate a browser
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        return headers

    def _get_proxies(self, max_attempts=5, delay=0.5):
        # Use a proxy to make requests

        for attempt in range(1, max_attempts + 1):
            try:
                req_proxy = RequestProxy()
                proxies = req_proxy.get_proxy_list()
                return {'http': proxies[0].get_address()}
            except Exception as e:
                print(f"Error fetching proxy list (Attempt {attempt}/{max_attempts}): {e}")
                time.sleep(delay)

        # If all attempts fail, return an empty list
        return []

    def _load_saved_rate(self):
        import os
        try:
            with open(settings.EXCHANGE_RATE['PATH'], 'rb') as file:
                # Check if the file is not empty before attempting to load
                if os.path.getsize(settings.EXCHANGE_RATE['PATH']) > 0:
                    saved_data = pickle.load(file)
                    return saved_data
                else:
                    # If the file is empty, return an empty dictionary
                    return {}
        except FileNotFoundError:
            # If the file is not found, return an empty dictionary
            return {}

    def _save_rate(self):
        with open(settings.EXCHANGE_RATE['PATH'], 'wb') as file:
            pickle.dump(self._response, file)

    def _rate_via_brh(self):
        # Check if the rate has been saved for today
        today = timezone.now()
        if 'brh_rate' in self._response and self._response['brh_rate']['date'] == today:
            return

        # Make request with fake headers and proxy
        headers = self._get_fake_headers()
        proxies = self._get_proxies()
        if proxies:
            content = requests.get('https://brh.ht', headers=headers, proxies=proxies, timeout=10)
        else:
            content = requests.get('https://brh.ht', headers=headers, timeout=10)

        # Parse HTML content
        bs = BeautifulSoup(content.text, 'html.parser')

        reference_td = bs.find('td', text='Taux de reference', attrs={'class': 'text-left imp'})

        if reference_td:
            # Extract the rate value from the next sibling td element
            rate_value = reference_td.find_next('td', class_='text-left').text
        else:
            rate_value = None

        rate_element = bs.find('td', class_='text-left imp')

        # Save rate and date
        self._response['brh_rate'] = {
            'rate': rate_value,
            'date': today,
        }

        # Save the new rate data
        self._save_rate()

    def _rate_via_api(self, _from):
        today = timezone.now()
        saved_data = self._load_saved_rate()

        if 'api_rate' in saved_data and saved_data['api_rate']['date'] == today:
            # Use the saved rate if it's already available for today
            self._response = saved_data
            return

        try:
            # Replace this URL with the actual endpoint of the exchange rate API you want to use
            api_key = '118f1ca6740f949b338e0dde'
            api_url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/{_from.upper()}'
            response = requests.get(api_url)
            data = response.json()

            # Extract the exchange rate for a specific currency
            exchange_rate = data['conversion_rates'].get('HTG')

            if exchange_rate is not None:
                self._response['api_rate'] = {
                    'rate': exchange_rate,
                    'date': today,
                }

                # Save the new rate data
                self._save_rate()
        except Exception as e:
            print(f"Error fetching exchange rate from API: {e}")

    def _rate_via_custom(self, _from):
        self._response['api_rate'] = {
            'rate': settings.EXCHANGE_RATE['CUSTOM'][_from],
        }

    def engine(self, _from='USD', system=settings.EXCHANGE_RATE['SYSTEM']):
        # Define a dictionary to map functions based on the provided arguments
        rate_functions = {
            '_rate_via_brh': self._rate_via_brh,
            '_rate_via_api': lambda: self._rate_via_api(_from),
            '_rate_via_custom': lambda: self._rate_via_custom(_from),
        }

        if system == 'CUSTOM' and settings.EXCHANGE_RATE.get('CUSTOM') is None:
            raise AttributeError('CUSTOM key is missing in EXCHANGE_RATE')

        # Call the appropriate function based on the provided argument
        rate_functions.get(f'_rate_via_{system.lower()}', lambda: None)()

        return self._response['api_rate']['rate']