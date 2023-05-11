import requests

mapping = [
"Kline open time",
"Open price",
"High price",
"Low price",
"Close price",
"Volume",
"Kline close time",
"Quote asset volume",
"Number of trades",
"Taker buy base asset volume",
"Taker buy quote asset volume",
"Unused field. Ignore." ]

def get_historical_data(symbol, interval, start_time, end_time):
    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': start_time,
        'endTime': end_time,
        'limit': 5  # Maximum limit per request (adjust as needed)
    }
    response = requests.get(url, params=params)
    
    fileJson = []

    if response.status_code == 200:
        data = response.json()
        for entry in data:
            fileJson.append({})
        return data
    else:
        return None

# Usage
symbol = 'BTCUSDT'  # Replace with your desired trading pair symbol
interval = '1d'     # Daily interval (adjust as needed)
start_time = 1620000000000  # Replace with your desired start time in milliseconds
end_time = 1650000000000    # Replace with your desired end time in milliseconds

historical_data = get_historical_data(symbol, interval, start_time, end_time)
if historical_data:
    # Process and analyze the historical data as needed
    print(historical_data)
else:
    print("Failed to retrieve historical data")
