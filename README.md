
# Historical data of currency exchange rate

Simple program that allows user to get historical currency exchange rate (data provided by https://currencyapi.com). To get started u need to create account on their website and save api key in json file: key.json, but remember that u have only 300 requests per month on free trial.



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
API version will run on your localhost on port 8000 (http://127.0.0.1:8000/ to use swagger u need to adjust docs#)

**Available endpoints**

| Endpoint | Description |
| --- | --- |
| 'currency_history' | Returns historical currency exchange rate of currencies and date specified by user |

## Examples:
**CLI version:**

![cli](https://github.com/jacobsoftware/currencyapi/blob/main/res/cli_example.PNG)

**FastAPI version (swagger) with correct parameters:**

![fastapi](https://github.com/jacobsoftware/currencyapi/blob/main/res/fastapi_correct_input.PNG)

**FastAPI version (swagger) with incorrect parameters:**

![fastapi](https://github.com/jacobsoftware/currencyapi/blob/main/res/fastapi_incorrect_input_example.PNG)
