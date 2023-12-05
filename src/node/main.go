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
	"log"
	"main/blockchainDataModel"
	mrand "math/rand"
	"net"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"
)

var (
	counter                      int
	balanceMap                   map[string]float64
	sigVerifyPort                string
	ammAdress                    string
	transactionBroadcastAddr     string
	localAddr                    string
	recievedTransactionHashes    []string
	transactionHandlingMulticast string
	blockHandlingMulticast       string
	privateKey                   *rsa.PrivateKey
	publicKey                    rsa.PublicKey
)

func setLocalVariables() {
	balanceMap = make(map[string]float64)
	balanceMap["BTC"] = 200
	balanceMap["ETH"] = 200

	conn, err := net.Dial("udp", "8.8.8.8:80")
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()

	localAddr = strings.Split(conn.LocalAddr().(*net.UDPAddr).String(), ":")[0]
	transactionBroadcastAddr = os.Getenv("TRANSACTION_BROADCAST")
	ammAdress = os.Getenv("AMM_SERVER_ADDR")
	privateKey, publicKey = blockchainDataModel.GenerateKeyPairAndReturn(localAddr)
	sigVerifyPort = os.Getenv("SIGNATURE_VERIFY_PORT")
	transactionHandlingMulticast = os.Getenv("TRANSACTION_BROADCAST")
	blockHandlingMulticast = os.Getenv("NODE_BROADCAST")
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
		// fmt.Println(transaction)
		fmt.Printf("Got Trans: %d\n", n)

		if !hasTransactionBeenUsed(transaction.TransactionHash) {
			val, _ := strconv.ParseFloat(transaction.Amount, 64)
			balanceMap[transaction.Token] += val
			recievedTransactionHashes = append(recievedTransactionHashes, transaction.TransactionHash)
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

// func getCurrencies() ([]string, error) {
// 	url := "http://" + ammAdress + "/get-currencies"

// 	// Send the GET request
// 	response, err := http.Get(url)
// 	if err != nil {
// 		log.Fatal("GET request failed:", err)
// 	}
// 	defer response.Body.Close()

// 	// Read the response body
// 	body, err := io.ReadAll(response.Body)
// 	// Print the response status code and body
// 	fmt.Println("Response Status:", response.Status)
// 	fmt.Println("Response Body:", string(body))

// 	var currencies []string
// 	err = json.Unmarshal(body, &currencies)
// 	return currencies, err
// }

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

func findMaxBalance() (string, float64) {
	var maxKey string
	var maxValue float64
	maxValue = -1
	for key, value := range balanceMap {
		if value > maxValue {
			maxKey = key
			maxValue = value
		}
	}
	return maxKey, maxValue
}

func trade() {
	for {
		counter += 1
		min := 1.0
		token, max := findMaxBalance()
		amount := min + mrand.Float64()*(max-min)
		balanceMap[token] -= amount

		var newTransaction = blockchainDataModel.Transaction{}
		newTransaction.Sender = localAddr
		newTransaction.Reciever = ammAdress
		newTransaction.Number = counter
		newTransaction.Amount = fmt.Sprintf("%f", amount)
		newTransaction.Token = token

		transactionbytes, _ := json.Marshal(newTransaction)
		transactionhash := blockchainDataModel.ReturnHash(transactionbytes)
		newTransaction.TransactionHash = hex.EncodeToString(transactionhash)
		sig, _ := rsa.SignPKCS1v15(crand.Reader, privateKey, crypto.SHA256, transactionhash)

		newTransaction.SenderSignature = hex.EncodeToString(sig)

		broadcastTransaction(newTransaction)
		time.Sleep(2 * time.Second)
	}
}

func publicKeyHandler(w http.ResponseWriter, r *http.Request) {
	pemBytes := pem.EncodeToMemory(&pem.Block{
		Type:  "PUBLIC KEY",
		Bytes: x509.MarshalPKCS1PublicKey(&publicKey),
	})

	// Write the public key as a response
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
	setLocalVariables()
	go httpHandler() //public key
	go handleTransactions()
	trade()
}
