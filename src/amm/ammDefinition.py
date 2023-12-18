import json, math, hashlib, csv, binascii
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from blockchainAdapter import BlockchainOrganizer

logFile = "log.csv"
fieldnames = ['BTCamount', 'ETHamount', 'BTCvETHrate']

class AmmClass:

    def __init__(self, filePath):

        self.private_key = rsa.generate_private_key(
            public_exponent=65537,  # Commonly used value for the public exponent
            key_size=2048  # Size of the key in bits
        )

        self.public_key = self.private_key.public_key()

        self.pem_private = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Serialize the public key to PEM format
        self.pem_public = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

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

        self.blockchain = BlockchainOrganizer()

    def getCurrencies(self):
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
    
    def requestedByConstantProduct(self, amount, token, exchangeToken):
        # minimal_part = 0.001 -> log10(minimal_part) = -3.0 -> round & abs -> 3 decimal numbers
        deimalRoundingDigits = abs(round(math.log10(self.currencies[token]["minimal_part"])))
        requested = self.currencies[exchangeToken]["amount"] - round(
            self.const_product_k / (amount + self.currencies[token]["amount"]), deimalRoundingDigits)
        return requested
    
    def requestedByConstantSum(self, amount, token, exchangeToken):
        # minimal_part = 0.001 -> log10(minimal_part) = -3.0 -> round & abs -> 3 decimal numbers
        deimalRoundingDigits = abs(round(math.log10(self.currencies[request.json["to"]]["minimal_part"])))
        requested = self.currencies[exchangeToken]["amount"] - round(
            self.const_sum_k - (amount + self.currencies[token]["amount"]), deimalRoundingDigits)
        return requested

    def proportional(self, amount, token, exchangeToken):
        # minimal_part = 0.001 -> log10(minimal_part) = -3.0 -> round & abs -> 3 decimal numbers
        deimalRoundingDigits = abs(round(math.log10(self.currencies[request.json["to"]]["minimal_part"])))
        factor = self.currencies[exchangeToken]["amount"] / self.currencies[token]["amount"]
        requested = round(amount * factor, deimalRoundingDigits)
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
    

    def performTransaction(self, request):
        print(request)
        amount = float(request["Amount"])
        token = request["Token"]
        exchangeToken = request["Metadata"]["ExchangeToken"]
        if "Metadata" in request:
            exchangeRate = float(request["Metadata"]["ExchangeRate"])
            maxSlippage = float(request["Metadata"]["MaxSlippage"])
        # requested = self.requestedByConstantProduct(request, self.const_product_k)
        requested = self.requestedByConstantProduct(amount, token, exchangeToken)
        returnTransaction = {}
        returnTransaction["TimeStamp"] = datetime.now().isoformat('T')
        returnTransaction["Sender"] = request["Reciever"]
        returnTransaction["Reciever"] = request["Sender"]

        newRate = requested / amount
        if "Metadata" in request and newRate / exchangeRate <= maxSlippage:
            #perform
            self.currencies[token]["amount"] += amount
            self.currencies[token]["volume"] += amount
            self.currencies[exchangeToken]["amount"] -= requested
            self.currencies[exchangeToken]["volume"] += requested

            self.transactions.insert(0, {"peer": request["Sender"], "from": token, "to": exchangeToken, "amountFrom": amount, "amountTo": requested})

            returnTransaction["Amount"] = str(requested)
            returnTransaction["Token"] = exchangeToken
        else:
            #reject
            returnTransaction["Amount"] = str(amount)
            returnTransaction["Token"] = token

        transactionHash = hashlib.sha256(str(returnTransaction).encode('UTF-8')).digest()
        returnTransaction["TransactionHash"] = binascii.hexlify(transactionHash).decode('utf-8')
        signature = self.private_key.sign(
            transactionHash,
            padding.PKCS1v15(),
            hashes.SHA256())
        returnTransaction["SenderSignature"] = binascii.hexlify(signature).decode('utf-8')
        return returnTransaction


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

    def addBlock(self, block):
        self.blockchain.addBlock(block)

    def getValidBlock(self):
        return self.blockchain.getValidBlock()

    def getAwaitingBlocks(self):
        return self.blockchain.getAwaitingBlocks()
    
    def getValidTransactions(self):
        return self.blockchain.getValidTransactions()