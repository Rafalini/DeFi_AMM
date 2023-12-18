import requests, json, os

def getPricesAndAmounts():

    API_KEY = os.getenv("APIKEY")
    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    # url2 = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'


    parameters = {
        'id': '1,1027,1839,52',
        # 'limit': 5000
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    }

    response = requests.get(url, headers=headers, params=parameters)
    data = response.json()

    return data
    
    

with open("marketCap1.json", "w") as file:
    json.dump(getPricesAndAmounts(), file)

# "price": 41695.71789016854,