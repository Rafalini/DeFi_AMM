import json, math
from datetime import datetime

class AmmClass:
 
    def __init__(self, filePath):
        config_file = open(filePath)
        self.config = json.load(config_file)
        self.currencies = {}
        self.transactions = []
        self.transactionCacheLimit = 8
        self.const_product_k = 1
        self.const_sum_k = 0

        for entry in self.config["currencies"]:
            self.currencies[entry["short"]] = {"amount":entry["amount"], "minimal_part": entry["minimal_part"], "volume": 0}
            self.const_product_k *= entry["amount"]
            self.const_sum_k += entry["amount"]

    def getCurrencies(self):
        # response = []
        # for entry in currencies:
        #     response.append(entry)
        return self.currencies.copy()
    
    def getCurrentAmounts(self):
        data = {}
        amounts = {}
        rates = {}
        for currency in self.currencies:
            amounts[currency] = self.currencies[currency]["amount"]
            if currency != "BTC":
                rates[currency] = self.currencies[currency]["amount"] / self.currencies["BTC"]["amount"]
        return data
    
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
        for currency in self.currencies:
            rates = {}
            for referenceCurrency in self.currencies:
                # if referenceCurrency != currency:
                rates[referenceCurrency] = self.currencies[referenceCurrency]["amount"] / self.currencies[currency]["amount"]
            response[currency] = rates
        return response
    

    def performTransaction(self, request):

        requested = self.requestedByConstantProduct(request, self.const_product_k)

        if self.currencies[request.json["to"]]["amount"] - requested > 0:

            self.currencies[request.json["from"]]["amount"] += request.json["amount"]
            self.currencies[request.json["from"]]["volume"] += abs(request.json["amount"])
            self.currencies[request.json["to"]]["amount"] -= requested
            self.currencies[request.json["to"]]["volume"] += abs(requested)

            # transactions = addTransaction(transactions, str(request.remote_addr)+" traded "+request.json["to"]["amount"] +" "+request.json["to"], transactionCacheLimit)
            self.transactions.insert(0,
                                {"peer": str(request.remote_addr), "from": request.json["from"], "to": request.json["to"],
                                "amountFrom": request.json["amount"], "amountTo": requested})
            # transactions.insert(0, str(request.remote_addr)+" traded "+str(round(requested,3)) +" "+str(request.json["to"])+"\n")
            if len(self.transactions) == self.transactionCacheLimit:
                self.transactions.pop(len(self.transactions) - 1)
                # self.transactions.pop()

            blockChainTransaction1={}
            blockChainTransaction1["sender"] = request.json["client"]
            blockChainTransaction1["reciever"] = "0xAMM"
            blockChainTransaction1["amount"] = request.json["amount"]
            blockChainTransaction1["token"] = "ECR17"
            blockChainTransaction1["sender_signature"] = "singature"
            blockChainTransaction2 = {}
            blockChainTransaction2["sender"] = "0xAMM"
            blockChainTransaction2["reciever"] = request.json["client"]
            blockChainTransaction2["amount"] = requested
            blockChainTransaction2["token"] = "ECR3"
            blockChainTransaction2["sender_signature"] = "singature"
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
        return self.transactions.copy()

    def getAmounts(self):
        amounts = {}
        for currency in self.currencies:
            amounts[currency] = self.currencies[currency]["amount"]
        return amounts