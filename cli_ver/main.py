import requests
import os
import json
import re
import time
from decimal import Decimal, ROUND_UP

# This function allows us to read data from json file
def load_json(file:str) ->list:
    with open(file, 'r') as json_file:
        key = json.load(json_file)
        return key

# Global variables    
FILE = os.path.join(os.path.dirname(__file__), 'key.json')   
API_KEY = load_json(FILE)
HEADERS = {'apikey': API_KEY['key']}
CURRENCIES_PATH = os.path.join(os.path.dirname(__file__), 'currencies.json')
URL_CURRENCIES = 'https://api.currencyapi.com/v3/currencies'
URL_HISTORY = 'https://api.currencyapi.com/v3/historical/'

REGEX_INPUT_CURRENCY = '^[A-Z]{2,4}$'
REGEX_OUTPUT_CURRENCY = '^([A-Z]{2,4},?){1,185}$'
REGEX_AMOUNT = '^[0-9]{1,100}\.?[0-9]{0,2}$'
REGEX_DATE = '^(1999|[2]{1}[0]{1}[012]{1}[0-9]{1})\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$'

# Decorator for api_request if something go wrong in first try, after 3 failed retries program will shutdown
def retry(function, retries=3):
    def wrapper(*args):
        attempts = 0
        while attempts < retries:
            try:
                return function(*args)
            
            except requests.exceptions.RequestException as error:
                print(error)
                time.sleep(2 + attempts*2)
                attempts += 1
                if attempts == 3: raise Exception('Something is wrong with server')

    return wrapper

# Function that will send our request    
@retry
def api_request(url: str, params=None) -> requests.models.Response:
    response = requests.get(url, headers=HEADERS, params=params)   
    return response

# Function that will read entire acronims of all available currencies (185) on currencyapi.com
def read_currencies(response: requests.models.Response) -> None:
    json_data = response.json()
    currencies_dict = {'currency':[]}

    for currency in json_data['data']:       
        currencies_dict['currency'].extend([currency])
    
    with open(CURRENCIES_PATH, 'w') as save_currencies:
        json.dump(currencies_dict, save_currencies)


# Function that will read user inputs and then will check values with regex cuz we don't want to send
# incorrect data via request cuz we are limited (300 api calls in free trial)     
def user_input(text_to_print: str,
                regex: str,
                input_currency = False,
                output_multiple_currency = False) -> str:
    
    while True:
        input_value = input(text_to_print)
        regex_search = re.search(regex, input_value)

        if regex_search:

            # Only for input currency and ouput currency
            if input_currency is not False or output_multiple_currency is not False:
                currency_acronym = load_json(CURRENCIES_PATH)

                # Only for input currency
                if input_value in currency_acronym['currency'] and input_currency is not False:
                    return input_value
                elif input_currency is not False: print('Program does not support this currency: ',input_value)

                # Only for output currency
                if output_multiple_currency is not False:
                    input_value_splitted = input_value.split(',')
                    if set(input_value_splitted).issubset(currency_acronym['currency']): return input_value
                    else: print('Program does not support this currency: ',set(input_value_splitted).difference(currency_acronym['currency']))

            # Only for date and amount
            else:
                return input_value
            
        else: 
            if 'amount' in text_to_print: print('Wrong amount format, program only allows two decimal places, also use dots instead of commas')
            elif 'date' in text_to_print: print('Correct format date is: YYYY-MM-DD and program provide only data since 1999')
            elif 'input' in text_to_print: print('Currency acronim should be written in block letters')
            else: print('Currency acronim should be written in block letters and use commas to separate them')
# This function will calculate amount of currency for output_currencies and then will print it
# After this program ends his work
def handle_output(params: dict,
                  amount: float) -> None:
    response_historical = api_request(URL_HISTORY, params)
    json_data = response_historical.json()
    
    print(f'\nData for {date}:')

    for value in json_data['data'].values():
        amount_in_output_currency = amount * value['value']
        output_currency_acronim = value['code']

        # Check for regular currencies
        if amount_in_output_currency >= 0.01:
            amount_in_output_currency = Decimal(amount_in_output_currency).quantize(Decimal('0.01'),rounding=ROUND_UP)
        
        # We need this rouding for eth and maybe other cryptocurrencies 1zl/eth = 00011
        elif amount_in_output_currency > 0.0001 and amount_in_output_currency < 0.01:
            amount_in_output_currency = Decimal(amount_in_output_currency).quantize(Decimal('0.0001'),rounding=ROUND_UP)
        
        # We need this rounding for bitcoin for example 1zl/btc = 0.0000059
        elif amount_in_output_currency > 0.000001 and amount_in_output_currency <= 0.0001:
            amount_in_output_currency = Decimal(amount_in_output_currency).quantize(Decimal('0.000001'),rounding=ROUND_UP)

        print(f' -> {amount} {params["base_currency"]} = {amount_in_output_currency} {output_currency_acronim}')

# Beware currencyapi.com can provide incorrect historical data, had issue with their Bitcoin value from 2021-2022
if __name__ == '__main__':

    if os.path.exists('currencies.json') is False: read_currencies(api_request(URL_CURRENCIES))

    input_currency = user_input('Enter input currency: ', REGEX_INPUT_CURRENCY, True)
    output_currency = user_input('Enter output currencies: ', REGEX_OUTPUT_CURRENCY, False, True)
    amount = float(user_input('Enter amount: ', REGEX_AMOUNT))
    date = user_input('Enter date: ', REGEX_DATE)

    params = {'date': date,
            'base_currency': input_currency, 
            'currencies': output_currency}
    handle_output(params, amount)

    