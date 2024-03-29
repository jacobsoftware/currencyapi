
# Historical data of currency exchange rate

Simple program that allows user to get historical currency exchange rate (data provided by https://currencyapi.com). To get started you need to create account on their website and save api key in json file: key.json, but remember that you have only 300 requests per month on free trial.



## Run Locally

**Clone the project:**

```bash
  git clone https://github.com/jacobsoftware/currencyapi
```

**To install the necessary packages:**

```bash
  pip install -r requirements.txt
```


**To run CLI version:**

```bash
  cd cli_ver && pip run python main.py
```

**To run API version:**

```bash
  cd fastapi_ver && uvicorn app:app --reload
```
API version will run on your localhost on port 8000 (http://127.0.0.1:8000/ or http://localhost:8000/ to use swagger u need to add docs# at the end of link: http://127.0.0.1:8000/doc#)

**Available endpoints:**

| Endpoint | Description |
| --- | --- |
| `currency_history` | Returns historical conversion based on user parameters |

**Parameters for currency_history endpoint:**

| Parameters | Description |
| --- | --- |
| `base_currency` | The currency that user wants to convert. Use acronyms of currencies, capitalized (185 currencies are available you can find them in currencies.json). **Required** |
| `currencies` | Currencies/currency the user wants to convert to. Use acronyms of currencies, capitalized if you want to get more than one currency, separate them with commas (185 currencies are available you can find them in currencies.json **Required** |
| `amount` | Amount of base currency that user want to convert. Remember to use dots instead of comma for decimal value. **Required** |
| `date` | Date of historical currency exchange rate. This should be in format: YYYY-MM-DD. Also https://currencyapi.com only provide data since 1999. **Required** |

## Examples:
**CLI version:**

![cli](https://github.com/jacobsoftware/currencyapi/blob/main/res/cli_example.PNG)

**FastAPI version (swagger) with correct parameters:**

![fastapi](https://github.com/jacobsoftware/currencyapi/blob/main/res/fastapi_correct_input.PNG)

**FastAPI version (swagger) with incorrect parameters:**

![fastapi](https://github.com/jacobsoftware/currencyapi/blob/main/res/fastapi_incorrect_input_example.PNG)
