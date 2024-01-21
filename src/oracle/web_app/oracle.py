import os, requests, threading, time, csv
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


class Oracle:
    def __init__(self):
        self.checkpoint_path = "./weights"
        self.logFile = "log/oracle_log.csv"
        addr = os.getenv("AMM_SERVER_ADDR")
        port = int(os.getenv("AMM_SERVER_PORT"))
        self.ammUrl = "http://"+addr+":"+str(port)

        self.currencyIds = self.getCurrencies()
        self.pricesTable = self.getPricesAndAmounts()

        self.fieldNames = ["time", self.pricesTable[0]["symbol"]+","+self.pricesTable[1]["symbol"]+","+self.pricesTable[2]["symbol"]]

        f = open(self.logFile, "w")
        f.write("time"+','+ self.pricesTable[0]["symbol"]+","+self.pricesTable[1]["symbol"]+","+self.pricesTable[2]["symbol"])
        f.write('\n')
        f.close()

        save_thread = threading.Thread(target=self.periodicSave, name="saver")
        save_thread.start()

    def getCurrencies(self):
        url1 = self.ammUrl+"/get-currencies"
        ids = ""
        try:
            response1 = requests.get(url1)
            for entry in response1["currencies"]:
                ids += entry["id"]+","
        except Exception:
            pass
        return ids

    def getPricesAndAmounts(self):
        API_KEY = os.getenv("APIKEY")
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
        usdPrices = []
        
        # usdPrices.append({"symbol" : data["data"]["1"]["symbol"], "usdprice" : data["data"]["1"]["quote"]["USD"]["price"] })
        usdPrices.append({"symbol" : data["data"]["1027"]["symbol"], "usdprice" :  data["data"]["1027"]["quote"]["USD"]["price"], "modificator":0 })
        usdPrices.append({"symbol" : data["data"]["5176"]["symbol"], "usdprice" :  data["data"]["5176"]["quote"]["USD"]["price"], "modificator":0 })
        usdPrices.append({"symbol" : data["data"]["1518"]["symbol"], "usdprice" :  data["data"]["1518"]["quote"]["USD"]["price"], "modificator":0 })

        return usdPrices

    def saveStep(self, start_time):
        pricesTable = self.pricesTable
        elapsed_time = time.time() - start_time
        elapsed_milliseconds = int(elapsed_time * 1000)

        fieldnames = ["time", pricesTable[0]["symbol"], pricesTable[1]["symbol"], pricesTable[2]["symbol"]]
        if elapsed_time < 60:
            with open(self.logFile, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if csvfile.tell() == 0:
                    writer.writeheader()

                data = {"time":elapsed_milliseconds,
                        pricesTable[0]["symbol"]:pricesTable[0]["usdprice"]+pricesTable[0]["modificator"], 
                        pricesTable[1]["symbol"]:pricesTable[1]["usdprice"]+pricesTable[0]["modificator"],
                        pricesTable[2]["symbol"]:pricesTable[2]["usdprice"]+pricesTable[0]["modificator"]}  # Replace with your data
                writer.writerow(data)
                csvfile.close()

    def periodicSave(self):
        start_time = time.time()
        while (time.time() - start_time) < 60:
            self.saveStep(start_time)
            time.sleep(1)

    def loadModel(self):
        print("Initialization of prediction model...")

        # model = Sequential()
        # model.add(LSTM(50, return_sequences = True, input_shape=(50, 1)))
        # model.add(LSTM(64, return_sequences = False))
        # model.add(Dense(1, activation='linear'))
        # model.compile(loss='mse', optimizer='rmsprop')
        # model.load_weights(self.checkpoint_path)

        print("Initialization done.")