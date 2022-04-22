import requests
import json
import os
from dotenv import load_dotenv

class Poe_trade:
    def __init__(self):
        load_dotenv()
        self.cookie = 'POESEDDID=' + os.getenv('POESESSID')

        self.headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'User-Agent': 'marcellusgaming@gmail.com',
                   'Cookie': self.cookie}

        self.bulk_exchange_url = 'https://www.pathofexile.com/api/trade/exchange/Archnemesis'

        self.fetch_url = 'https://www.pathofexile.com/api/trade/fetch/'


    def price_check_bulk(self, item, listings_to_print):
        """
        Checks how many of an item you need to bulk sell them for one exalt by returning a list of several listings in the bulk exchange
        :param item: item to price check (must be a valid exchange tag) https://www.pathofexile.com/trade/about
        :param listings_to_print: How many listings that will be returned
        :return: list of tuples (x, y) where x is the bulk price in exalts and y is amount of item the seller has in stock
        """
        bulk_dict = {
            'exchange': {
                'status': {
                    'option': 'onlineleague'
                },
                'have': ['exalted'],
                'want': [item],
                'minimum': 1,
                'fulfillable': True
            }
        }

        bulk_data = json.dumps(bulk_dict)

        r = requests.post(self.bulk_exchange_url,
                          headers=self.headers,
                          data=bulk_data)

        response_json = r.json()

        bulk_listings = response_json['result'][:listings_to_print]
        query_id = response_json['id']
        fetch_data = {'query': query_id, 'exchange': True}

        r = requests.get(self.fetch_url + ','.join(bulk_listings),
                         headers=self.headers,
                         data=fetch_data)

        listings_list = []

        for listing in r.json()['result']:
            # Get note, which contains bulk exalt price
            price = listing['item']['note'].split(' ')[1]
            # Get stock
            stock = int(listing['item']['properties'][0]['values'][0][0].split('/')[0])
            listings_list.append((price, stock))

        return listings_list

trade = Poe_trade()
print(trade.price_check_bulk('ancient-orb', 5))