package main

import (
	"crypto"
	crand "crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/hex"
	"encoding/json"
	"encoding/pem"
	"fmt"
	"io/ioutil"
	"log"
	"main/blockchainDataModel"
	"main/metrics"
	"math/rand"
	"net"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"
)

var (
	// counter                      int
	balanceMap                   map[string]float64
	sigVerifyPort                string
	ammAdress                    string
	ammPort                      string
	oracleAdress                 string
	transactionBroadcastAddr     string
	localAddr                    string
	recievedTransactionHashes    []string
	transactionHandlingMulticast string
	logFile                      string
	privateKey                   *rsa.PrivateKey
	publicKey                    rsa.PublicKey
)

type RatesResponse struct {
	// BTC  map[string]float64 `json:"BTC"`
	ETH  map[string]float64 `json:"ETH"`
	MKR  map[string]float64 `json:"MKR"`
	XAUt map[string]float64 `json:"XAUt"`
	Time string             `json:"time"`
}

func setLocalVariables() {
	balanceMap = make(map[string]float64)
	// balanceMap["BTC"] = 3000
	balanceMap["ETH"] = 3000
	balanceMap["XAUt"] = 3000
	balanceMap["MKR"] = 3000

	conn, err := net.Dial("udp", "8.8.8.8:80")
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()

	localAddr = strings.Split(conn.LocalAddr().(*net.UDPAddr).String(), ":")[0]
	transactionBroadcastAddr = os.Getenv("TRANSACTION_BROADCAST")
	ammAdress = os.Getenv("AMM_SERVER_ADDR")
	ammPort = os.Getenv("AMM_SERVER_PORT")
	oracleAdress = os.Getenv("ORA_SERVER_ADDR") + ":" + os.Getenv("ORA_SERVER_PORT")
	privateKey, publicKey = blockchainDataModel.GenerateKeyPairAndReturn("log/keys/" + localAddr)
	sigVerifyPort = os.Getenv("SIGNATURE_VERIFY_PORT")
	transactionHandlingMulticast = os.Getenv("TRANSACTION_BROADCAST")
	logFile = "log/" + strings.Split(localAddr, ":")[0] + os.Getenv("METRICS_FILE")
	metrics.PrepareLog(logFile)
}

func getPrices() map[string]float64 {
	url := "http://" + oracleAdress + "/get-prices" // Replace with your API endpoint URL

	// Make the GET request
	resp, err := http.Get(url)
	if err != nil {
		fmt.Println("Error making GET request:", err)
		return nil
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Println("Unexpected status code:", resp.StatusCode)
		return nil
	}

	// Read the response body
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Error reading response body:", err)
		return nil
	}

	var data []map[string]interface{}

	// Unmarshal JSON into a slice of maps
	err = json.Unmarshal([]byte(body), &data)
	if err != nil {
		fmt.Println("Error:", err)
		return nil
	}

	// Create a map to store symbol as key and usdprice as value
	symbolPriceMap := make(map[string]float64)

	// Iterate through the array and populate the map
	for _, item := range data {
		if symbol, ok := item["symbol"].(string); ok {
			if usdPrice, ok := item["usdprice"].(float64); ok {
				symbolPriceMap[symbol] = usdPrice
			}
		}
	}
	// fmt.Println(symbolPriceMap)
	return symbolPriceMap
}

func getRates() map[string]map[string]float64 {
	url := "http://" + ammAdress + ":" + ammPort + "/get-rates" // Replace with your API endpoint URL

	// Make the GET request
	resp, err := http.Get(url)
	if err != nil {
		fmt.Println("Error making GET request:", err)
		return nil
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Println("Unexpected status code:", resp.StatusCode)
		return nil
	}

	// Read the response body
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Error reading response body:", err)
		return nil
	}

	var data RatesResponse

	// Unmarshal the JSON into the struct
	if err := json.Unmarshal(body, &data); err != nil {
		fmt.Println("Error unmarshalling JSON:", err)
		return nil
	}
	fmt.Println(data)

	ratesMap := make(map[string]map[string]float64)
	// ratesMap["BTC"] = data.BTC
	ratesMap["ETH"] = data.ETH
	ratesMap["MKR"] = data.MKR
	ratesMap["XAUt"] = data.XAUt

	return ratesMap
}

func handleTransactions() {
	addr, _ := net.ResolveUDPAddr("udp", transactionHandlingMulticast)
	conn, _ := net.ListenMulticastUDP("udp", nil, addr)

	defer conn.Close()

	buffer := make([]byte, 1024)

	fmt.Println("Listening for multicast transactions on", transactionHandlingMulticast)

	// Infinite loop to listen for multicast messages
	for {
		n, _, err := conn.ReadFromUDP(buffer)
		if err != nil {
			fmt.Println("Error reading from UDP connection:", err)
			continue
		}

		var transaction = blockchainDataModel.Transaction{}
		json.Unmarshal(buffer[:n], &transaction)

		if !hasTransactionBeenUsed(transaction.TransactionHash) && transaction.Reciever == localAddr {
			fmt.Printf("Recieved transaction: " + transaction.Token + " " + transaction.Amount)
			val, _ := strconv.ParseFloat(transaction.Amount, 64)
			balanceMap[transaction.Token] += val
			recievedTransactionHashes = append(recievedTransactionHashes, transaction.TransactionHash)
			metrics.UpdateLog(balanceMap, getPrices(), logFile)
		}
	}
}

func hasTransactionBeenUsed(target string) bool {
	for _, element := range recievedTransactionHashes {
		if element == target {
			return true // Found the target string in the list
		}
	}
	return false // Target string not found in the list
}

func broadcastTransaction(transaction blockchainDataModel.Transaction) {
	udpAddr, err := net.ResolveUDPAddr("udp", transactionBroadcastAddr)
	if err != nil {
		fmt.Println("Error resolving UDP address:", err)
		os.Exit(1)
	}

	conn, err := net.DialUDP("udp", nil, udpAddr)
	if err != nil {
		fmt.Println("Error creating UDP connection:", err)
		os.Exit(1)
	}
	defer conn.Close()

	blockStr, _ := json.Marshal(transaction)
	_, err = conn.Write(blockStr)
	if err != nil {
		fmt.Println("Error sending data:", err)
		os.Exit(1)
	}
}

func calculateMaxGain() (string, string, float64) {
	// min := 1.0
	// token, max := findMaxBalance()
	// exchangeTokens := getKeysExcept(token)
	// amount := min + mrand.Float64()*(max-min)

	maxToken := ""
	maxEchangeToken := ""
	maxGain := 0.0

	priceMap := getPrices() //key - value
	rateMap := getRates()   // key - key value

	for token := range priceMap {
		for referenceToken := range priceMap {
			if token == referenceToken {
				continue
			}

			gain := priceMap[token]*balanceMap[token] - balanceMap[referenceToken]*priceMap[referenceToken]*rateMap[token][referenceToken]
			if maxGain < gain {
				maxGain = gain
				maxToken = token
				maxEchangeToken = referenceToken
			}

		}
	}
	min := 1.0
	max := balanceMap[maxToken] / 4
	amount := min + rand.Float64()*(max-min)
	return maxToken, maxEchangeToken, amount
}

func trade() {
	for {
		token, exchangeToken, amount := calculateMaxGain()
		balanceMap[token] -= amount

		var newTransaction = blockchainDataModel.Transaction{}
		newTransaction.Sender = localAddr
		newTransaction.Reciever = ammAdress
		var timeStamp = time.Now()
		newTransaction.TimeStamp = timeStamp.Format("2006-01-02T15:04:05.999999999Z07:00")
		newTransaction.Amount = fmt.Sprintf("%f", amount)
		newTransaction.Token = token
		newTransaction.Metadata.ExchangeToken = exchangeToken
		newTransaction.Metadata.MaxSlippage = fmt.Sprintf("%f", 100000.0)
		newTransaction.Metadata.ExchangeRate = fmt.Sprintf("%f", 1.0)

		transactionbytes, _ := json.Marshal(newTransaction)
		transactionhash := blockchainDataModel.ReturnHash(transactionbytes)
		newTransaction.TransactionHash = hex.EncodeToString(transactionhash)
		sig, _ := rsa.SignPKCS1v15(crand.Reader, privateKey, crypto.SHA256, transactionhash)

		newTransaction.SenderSignature = hex.EncodeToString(sig)

		broadcastTransaction(newTransaction)
		time.Sleep(500 * time.Millisecond)
	}
}

func getKeysExcept(token string) []string {
	keys := make([]string, 0, len(balanceMap)-1)
	for key := range balanceMap {
		if key != token {
			keys = append(keys, key)
		}
	}
	shuffleKeys(keys)
	return keys
}

func shuffleKeys(keys []string) {
	rand.Shuffle(len(keys), func(i, j int) {
		keys[i], keys[j] = keys[j], keys[i]
	})
}

func publicKeyHandler(w http.ResponseWriter, r *http.Request) {
	pemBytes := pem.EncodeToMemory(&pem.Block{
		Type:  "PUBLIC KEY",
		Bytes: x509.MarshalPKCS1PublicKey(&publicKey),
	})
	w.Header().Set("Content-Type", "application/x-pem-file") // Set the appropriate content type
	w.Write(pemBytes)
}

func httpHandler() {
	http.HandleFunc("/get-public-key", publicKeyHandler)
	fmt.Println("Server is running: /get-public-key")
	err := http.ListenAndServe(":"+sigVerifyPort, nil)
	if err != nil {
		fmt.Println("Error starting server:", err)
	}
}

func main() {
	time.Sleep(2 * time.Second)
	setLocalVariables()
	go httpHandler() //public key
	go handleTransactions()
	trade()
}
