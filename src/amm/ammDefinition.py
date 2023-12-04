import json, math, hashlib, csv
from datetime import datetime

logFile = "log.csv"
fieldnames = ['BTCamount', 'ETHamount', 'BTCvETHrate']

class AmmClass:
 
    def __init__(self, filePath):
        config_file = open(filePath)
        self.config = json.load(config_file)
        self.currencies = {}
        self.transactions = []
        self.pendingTransactions = []
        self.transactionCacheLimit = 8
        self.const_product_k = 1
        self.const_sum_k = 0
        f = open(logFile, "w")
        f.write("BTCamount,ETHamount,BTCvETHrate")
        f.close()

        for entry in self.config["currencies"]:
            self.currencies[entry["short"]] = {"amount":entry["amount"], "minimal_part": entry["minimal_part"], "volume": 0}
            self.const_product_k *= entry["amount"]
            self.const_sum_k += entry["amount"]

    def getCurrencies(self):
        # response = []
        # for entry in self.currencies:
        #     print(entry)
        #     response.append({"currency":entry, "data":self.currencies[entry]})
        return self.currencies.copy()
    
    def getAmounts(self):
        self.saveStep()    
        amounts = {}

        btcSum, ethSum = 0,0
        n = 30
        if len(self.pendingTransactions)>n:
            for transaction in self.pendingTransactions[-n:]:
                if transaction["sender"] == "0xAMM":
                    if transaction["token"] == "BTC":
                        btcSum -= transaction["amount"]
                    if transaction["token"] == "ETH":
                        ethSum -= transaction["amount"] 
                if transaction["reciever"] == "0xAMM":
                    if transaction["token"] == "BTC":
                        btcSum += transaction["amount"]
                    if transaction["token"] == "ETH":
                        ethSum += transaction["amount"] 

        for currency in self.currencies:
            if currency == "BTC":
                amounts[currency] = self.currencies[currency]["amount"] - btcSum
            if currency == "ETH":
                amounts[currency] = self.currencies[currency]["amount"] - ethSum
        return amounts
    
    def requestedByConstantProduct(self, request, const_k):
        # minimal_part = 0.001 -> log10(minimal_part) = -3.0 -> round & abs -> 3 decimal numbers
        deimalRoundingDigits = abs(round(math.log10(self.currencies[request.json["to"]]["minimal_part"])))
        requested = self.currencies[request.json["to"]]["amount"] - round(
            const_k / (request.json["amount"] + self.currencies[request.json["from"]]["amount"]), deimalRoundingDigits)
        return requested
    
    def requestedByConstantSum(self, request, const_k):
        # minimal_part = 0.001 -> log10(minimal_part) = -3.0 -> round & abs -> 3 decimal numbers
        deimalRoundingDigits = abs(round(math.log10(self.currencies[request.json["to"]]["minimal_part"])))
        requested = self.currencies[request.json["to"]]["amount"] - round(
            const_k - (request.json["amount"] + self.currencies[request.json["from"]]["amount"]), deimalRoundingDigits)
        return requested

    def proportional(self, request):
        # minimal_part = 0.001 -> log10(minimal_part) = -3.0 -> round & abs -> 3 decimal numbers
        deimalRoundingDigits = abs(round(math.log10(self.currencies[request.json["to"]]["minimal_part"])))
        factor = self.currencies[request.json["to"]]["amount"] / self.currencies[request.json["from"]]["amount"]
        requested = round(request.json["amount"] * factor, deimalRoundingDigits)
        return requested
    

    def getRates(self):
        response = {}    
        response["time"] = datetime.now().strftime("%H:%M:%S")
        list = self.getCurrentAmounts()
        # print(list)
        for currency in list:
            rates = {}
            for referenceCurrency in list:
                if referenceCurrency != currency:
                    rates[referenceCurrency] = list[referenceCurrency] / list[currency]
            response[currency] = rates
        return response
    
    # def saveRates(self):
    #     file = "rates.json"
    

    def performTransaction(self, request):
        requested = self.requestedByConstantProduct(request, self.const_product_k)

        if self.currencies[request.json["to"]]["amount"] - requested > 0:

            self.currencies[request.json["from"]]["amount"] += request.json["amount"]
            self.currencies[request.json["from"]]["volume"] += abs(request.json["amount"])
            self.currencies[request.json["to"]]["amount"] -= requested
            self.currencies[request.json["to"]]["volume"] += abs(requested)

            # transactions = addTransaction(transactions, request.getClientAddress().host+" traded "+request.json["to"]["amount"] +" "+request.json["to"], transactionCacheLimit)
            self.transactions.insert(0,
                                {"peer": request.getClientAddress().host, "from": request.json["from"], "to": request.json["to"],
                                "amountFrom": request.json["amount"], "amountTo": requested})
            # transactions.insert(0, request.getClientAddress().host+" traded "+str(round(requested,3)) +" "+str(request.json["to"])+"\n")
            # if len(self.transactions) == self.transactionCacheLimit:
                # self.transactions.pop(len(self.transactions) - 1)
                # self.transactions.pop()

            blockChainTransaction1={}
            blockChainTransaction1["sender"] = request.json["client"]
            blockChainTransaction1["reciever"] = "0xAMM"
            blockChainTransaction1["amount"] = request.json["amount"]
            blockChainTransaction1["token"] = request.json["from"]
            blockChainTransaction1["sender_signature"] = hashlib.sha256(str(blockChainTransaction1).encode('UTF-8')).hexdigest()
            blockChainTransaction2 = {}
            blockChainTransaction2["sender"] = "0xAMM"
            blockChainTransaction2["reciever"] = request.json["client"]
            blockChainTransaction2["amount"] = requested
            blockChainTransaction2["token"] = request.json["to"]
            blockChainTransaction2["sender_signature"] = hashlib.sha256(str(blockChainTransaction1).encode('UTF-8')).hexdigest()
            self.pendingTransactions.append(blockChainTransaction1)
            self.pendingTransactions.append(blockChainTransaction2)
            return [blockChainTransaction1, blockChainTransaction2]
        else:
            return []

    def lastTransactionChanges(self):
        changes = []
        if len(self.transactions) > 0:
            transaction = self.transactions[0]
            price = self.currencies[transaction["from"]]["amount"] / self.currencies[transaction["to"]]["amount"]
            lastPrice = (self.currencies[transaction["from"]]["amount"] - transaction["amountFrom"]) / (self.currencies[transaction["to"]]["amount"] + transaction["amountTo"])

            volumeChange = transaction["amountFrom"] / self.currencies[transaction["from"]]["volume"]
            priceChange = (price - lastPrice)/price

            changes.append({"currency":transaction["from"], "volume": round(self.currencies[transaction["from"]]["volume"],3), "volumeChange": round(volumeChange*100,5),
                            "price": round(price,3), "change": round(priceChange*100, 3)})

            price = self.currencies[transaction["to"]]["amount"] / self.currencies[transaction["from"]]["amount"]
            lastPrice = (self.currencies[transaction["to"]]["amount"] - transaction["amountTo"]) / (self.currencies[transaction["from"]]["amount"] + transaction["amountFrom"])

            volumeChange = transaction["amountTo"] / self.currencies[transaction["to"]]["volume"]
            priceChange = (lastPrice - price)/price

            changes.append({"currency":transaction["to"], "volume": round(self.currencies[transaction["to"]]["volume"],3), "volumeChange": round(volumeChange*100,5),
                            "price": round(price,3), "change": round(priceChange*100, 3)})
        return changes
    
    def getTransactions(self):
        return self.transactions

    def getCurrentAmounts(self):
        amounts = {}
        for currency in self.currencies:
            amounts[currency] = self.currencies[currency]["amount"]
        return amounts
    
    def saveStep(self):
        with open(logFile, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if csvfile.tell() == 0:
                writer.writeheader()

            ls = self.getCurrentAmounts()
            rates = self.getRates()

            data = {fieldnames[0]: ls["BTC"], fieldnames[1]:ls["ETH"], fieldnames[2]: rates["BTC"]["ETH"]}  # Replace with your data
            writer.writerow(data)
            csvfile.close()