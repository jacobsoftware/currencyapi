from fastapi import FastAPI

import main

app = FastAPI()

@app.get('/currency_history/')
def get_currency_history(input_currency: str,
                        output_currency: str,
                        amount: str,
                        date: str):
    
    params = {'base_currency': input_currency,
            'currencies': output_currency,
            'amount':amount, 
            'date': date}
    status_error = main.user_check_parameters(params,main.DICT_REGEX)

    if status_error:
        return status_error
    
    params.pop('amount')
    api_response = main.create_api_response(params,float(amount))
    return api_response
