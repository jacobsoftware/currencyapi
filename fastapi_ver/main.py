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
DICT_REGEX = {'regex_input_currency':REGEX_INPUT_CURRENCY,'regex_output_currency':REGEX_OUTPUT_CURRENCY,
              'regex_amount': REGEX_AMOUNT,'regex_date':REGEX_DATE}

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

def user_check_parameters(user_parameters: dict,
               regex_dict: dict) -> str:
    
    for (parameter_name,parameter_value),(regex_name,regex) in zip(user_parameters.items(),regex_dict.items()):
        
        regex_search = re.search(regex, parameter_value)

        if regex_search:

            # Only for input currency and ouput currency
            if parameter_name == 'input_currency' or parameter_name == 'output_currency':
                currency_acronym = load_json(CURRENCIES_PATH)

                # Only for input currency
                if parameter_value in currency_acronym['currency'] and parameter_name == 'input_currency':
                    pass
                elif parameter_name != 'output_currency': 
                    return {'Error':'Program does not support this currency: '+parameter_value}

                # Only for output currency
                if parameter_name == 'output_currency':
                    input_value_splitted = parameter_value.split(',')
                    if set(input_value_splitted).issubset(currency_acronym['currency']): pass
                    else: 
                        return {'Error':'Program does not support this currency: '+set(input_value_splitted).difference(currency_acronym['currency'])}

            # Only for date and amount
            else:
                pass
            
        else: 
            if 'amount' in parameter_name: return {'Error':'Wrong amount format, program only allows two decimal places, also use dots instead of commas'}
            elif 'date' in parameter_name: return {'Error':'Correct format date is: YYYY-MM-DD and program provide only data since 1999'}
            elif 'base' in parameter_name: return {'Error': 'Currency acronim should be written in block letters'}
            else: return {'Error': 'Currency acronim should be written in block letters and use commas to separate them'}

# This function will calculate amount of currency for output_currencies and then will create dict for api endpoint
def create_api_response(params: dict, amount: float) -> list:
    response_historical = api_request(URL_HISTORY, params)
    json_data = response_historical.json()
    api_response= []
    
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

        response_element = {'currency':output_currency_acronim,'amount':amount_in_output_currency}
        api_response.append(response_element)

    return api_response

if os.path.exists('currencies.json') is False: read_currencies(api_request(URL_CURRENCIES))

if __name__ == '__main__':
    pass