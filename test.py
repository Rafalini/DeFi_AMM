import requests, json, os

def getPricesAndAmounts():

    API_KEY = os.getenv("APIKEY")
    API_KEY = "a97a2391-8600-4c3e-8dbf-046dd9d86214"
    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    # url2 = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'


    parameters = {
        'id': '1027,1518,5176',
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

# import matplotlib.pyplot as plt
# import numpy as np

# y1 = np.array([3, 8, 1, 10, 15])
# y2 = np.array([6, 2, 7, 11, 15])
# x = np.array([0, 1, 2, 4, 3])


# plt.plot(x,y1)
# plt.plot(x,y2)

# plt.show()