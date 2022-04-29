import requests
import json
import os
from dotenv import load_dotenv


class PoeTrade:

    def __init__(self):
        load_dotenv()
        self.cookie = 'POESEDDID=' + os.getenv('POESESSID')
        self.league = os.getenv('POE_LEAGUE')

        self.headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'User-Agent': 'marcellusgaming@gmail.com',
                   'Cookie': self.cookie}

        self.bulk_exchange_url = f'https://www.pathofexile.com/api/trade/exchange/{self.league}'

        self.fetch_url = 'https://www.pathofexile.com/api/trade/fetch/'

        self.bulk_query = {
            'exchange': {
                'status': {
                    'option': 'onlineleague'
                },
                'have': [],
                'want': [],
                'minimum': 1,
                'fulfillable': True
            }
        }

        self.ninja_url = 'https://poe.ninja/api/data/currencyoverview'

        self.ninja_data = {
            'league': self.league,
            'type': None
        }

        self.breachstones = (
            'Chayula',
            'Uul-Netol',
            'Tul',
            'Esh',
            'Xoph',
        )

        self.breachstone_levels = (
            'Flawless',
            'Pure',
            'Enriched',
            'Charged',
            'Vanilla'
        )

    def __query(self, query_data, listings_to_get):
        data = json.dumps(query_data)
        r = requests.post(self.bulk_exchange_url, headers=self.headers, data=data)
        response_json = r.json()

        bulk_listings = response_json['result'][:listings_to_get]
        query_id = response_json['id']
        fetch_data = {'query': query_id, 'exchange': True}

        r = requests.get(self.fetch_url + ','.join(bulk_listings),
                         headers=self.headers,
                         data=fetch_data)

        return r.json()['result']

    def price_check_bulk_ex(self, item, listings_to_print):
        """
        Checks how many of an item you need to bulk sell them for one exalt by returning a list of several listings in the bulk exchange
        :param item: item to price check (must be a valid exchange tag) https://www.pathofexile.com/trade/about
        :param listings_to_print: How many listings that will be returned
        :return: list of tuples of strings (x, y) where x is the bulk price in exalts and y is amount of item the seller has in stock
        """

        bulk_data = self.bulk_query.copy()
        bulk_data['exchange']['have'].append('exalted')
        bulk_data['exchange']['want'].append(item)

        query_result = self.__query(bulk_data, listings_to_print)

        listings_list = []

        for listing in query_result:
            # Get note, which contains bulk exalt price
            price = listing['item']['note'].split(' ')[1]
            # Get stock
            stock = int(listing['item']['properties'][0]['values'][0][0].split('/')[0])
            listings_list.append((price, stock))

        return listings_list

    def price_check_bulk_chaos(self, item, min_stock, listings_to_print):
        """
        Queries the bulk exchange API for the item you want in chaos orbs.
        :param item: item to price check (must be a valid exchange tag) https://www.pathofexile.com/trade/about
        :param min_stock: minimum stock to filter for
        :param listings_to_print: how many listings that will be returned
        :return: list of tuples of strings (x, y) where x is the bulk price and y is the individual price
        """

        bulk_data = self.bulk_query.copy()
        bulk_data['exchange']['have'].append('chaos')
        bulk_data['exchange']['want'].append(item)
        bulk_data['exchange']['minimum'] = min_stock

        query_result = self.__query(bulk_data, listings_to_print)

        listings_list = []

        for listing in query_result:
            # Get price
            price = float(listing['listing']['price']['amount'])
            # Get note, which contains bulk price
            note = listing['item']['note'].split(' ')[1]
            listings_list.append((note, price))

        return listings_list

    def ninja_get_exalt_price(self):
        """
        Queries poe.ninja's API to get the current exalt price, rounded and unrounded.
        :return: Tuple (x, y) where x is the rounded and y the unrounded current exalt prices.
        """
        params = self.ninja_data.copy()
        params['type'] = 'Currency'
        result = requests.get(self.ninja_url, params=params)

        for item in result.json()['lines']:
            if item['currencyTypeName'] == 'Exalted Orb':
                ex_price = float(item['chaosEquivalent'])
                return round(ex_price), ex_price

    def exalt_to_chaos(self, exalts):
        """
        Converts given number of exalts into its chaos-equivalent price.
        Retrieves current exalt price from poe.ninja.
        :param exalts: Number of exalts to convert (can use decimals).
        :return: Chaos-equivalent price.
        """
        ex_price = self.ninja_get_exalt_price()[0]
        return round(ex_price * exalts), ex_price

    def ninja_get_fragments(self):
        """
        Queries poe.ninja's API to get the current price of all fragments.
        :return: dict representing the JSON query result.
        """
        params = self.ninja_data.copy()
        params['type'] = 'Fragment'
        result = requests.get(self.ninja_url, params=params)

        return result.json()['lines']

    def get_breachstones(self):
        """
        Checks the price of all breachstones.
        :return: dict of dicts containing the price of all breachstones, organized into lords and tiers.
        """
        breach_dict = {breachlord: {tier: 0 for tier in self.breachstone_levels}
                           for breachlord in self.breachstones}
        fragments = self.ninja_get_fragments()
        for item in fragments:
            item_name = item['currencyTypeName'].split(' ')
            if item_name[-1] == 'Breachstone':
                breach_dict[item_name[0][:-2]][item_name[1] if item_name[1] != 'Breachstone' else 'Vanilla'] = item['chaosEquivalent']
        return breach_dict

#trade = PoeTrade()
#print(trade.price_check_bulk_chaos('stacked-deck', 100, 5))
#print(trade.exalt_to_chaos(3))
#print(trade.get_breachstones())