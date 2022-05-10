import requests
import json
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup as soup


class PoeCog:

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
        self.ninja_url_item = 'https://poe.ninja/api/data/itemoverview'

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
        self.poelab_url = 'https://www.poelab.com/'

        # Setting a custom user agent apparently spoofs CloudFlare?
        self.poelab_headers = {
            'User-Agent': 'marcellusgaming@gmail.com'
        }

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

    def ninja_heist_gems(self, heist_gems):
        """
        Searches poe.ninja's skill gem listings and returns the prices of all gems matching the name.
        Corrupted (including 21 or 23q gems), awakened, and normal gems are ignored.
        :param gem: Name of the gem
        :return: dict containing the gem names and their prices
        """
        heist_gems = [gem.lower() for gem in heist_gems]

        params = self.ninja_data.copy()
        params['type'] = 'SkillGem'
        result = requests.get(self.ninja_url_item, params=params)
        gems = result.json()['lines']
        answer = {}
        for entry in gems:
            gem_name = entry['name']
            gem_level = entry['gemLevel']
            if any(list(map(lambda gem: gem in gem_name.lower(), heist_gems))):
                if 'Awakened' in gem_name:
                    continue
                if 'corrupted' in entry.keys():
                    continue
                if gem_level < 16:
                    continue
                if 'Phantasmal' not in gem_name and 'Anomalous' not in gem_name and 'Divergent' not in gem_name:
                    continue
                answer[f'{gem_level} {gem_name}'] = entry['chaosValue']

        answer_copy = answer.copy()
        levels = ['17', '18', '19', '20']
        for level in levels:
            for gem in answer_copy.keys():
                if level in gem:
                    if '16 ' + gem[3:] in answer.keys():
                        answer.pop(gem)

        return answer


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

    def get_lab(self, tier):
        """
        Gets current Lab layout of the given tier.
        :param tier: 0 to 3, 0 meaning Normal Lab, 3 being Uberlab. Check input before calling.
        :return: Link to the image containing the Lab layout.
        """

        def tier_string(tier):
            return {
                0: 'Normal',
                1: 'Cruel',
                2: 'Merciless',
                3: 'Uber'
            }[tier]
        find_string = tier_string(tier) + ' Labyrinth Daily Notes'

        # Get link to Uberlab's page from the main page (Uberlab page changes every reset)
        poelab_main_page = requests.get(self.poelab_url, headers=self.poelab_headers)
        main_page_parsed = soup(poelab_main_page.content, 'html.parser')
        lab_li = main_page_parsed.find(lambda tag: tag.string == find_string)
        lab_url = lab_li.a['href']

        lab_page = requests.get(lab_url, headers=self.poelab_headers)
        lab_page_parsed = soup(lab_page.content, 'html.parser')
        return lab_page_parsed.find(id='notesImg')['src']