package main

import (
	"crypto/rsa"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"main/blockchainDataModel"
	"math/rand"
	"net"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"
)

var (
	counter                  int
	sigVerifyPort            string
	ammAdress                string
	transactionBroadcastAddr string
	localAddr                string
	privateKey               *rsa.PrivateKey
	publicKey                rsa.PublicKey
)

func setLocalVariables() {
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
}

func getCurrencies() ([]string, error) {
	url := "http://" + ammAdress + "/get-currencies"

	// Send the GET request
	response, err := http.Get(url)
	if err != nil {
		log.Fatal("GET request failed:", err)
	}
	defer response.Body.Close()

	// Read the response body
	body, err := io.ReadAll(response.Body)
	// Print the response status code and body
	fmt.Println("Response Status:", response.Status)
	fmt.Println("Response Body:", string(body))

	var currencies []string
	err = json.Unmarshal(body, &currencies)
	return currencies, err
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

func trade() {
	var currencies [2]string
	currencies[0] = "BTC"
	currencies[1] = "ETH"
	for {
		counter += 1

		var newTransaction = blockchainDataModel.Transaction{}
		newTransaction.Sender = localAddr
		newTransaction.Reciever = ammAdress
		newTransaction.Number = counter
		min := 1
		max := 50
		newTransaction.Amount = strconv.Itoa(rand.Intn(max-min+1) + min)
		newTransaction.Token = currencies[0]
		transactionBytes, _ := json.Marshal(newTransaction)
		newTransaction.TransactionHash = hex.EncodeToString(blockchainDataModel.ReturnHash(transactionBytes))
		newTransaction.SenderSignature = hex.EncodeToString(blockchainDataModel.Sign(privateKey, []byte(newTransaction.TransactionHash)))

		// fmt.Println(newTransaction.TransactionHash)
		broadcastTransaction(newTransaction)
		time.Sleep(2 * time.Second)
		// signature := crypto.sign()
	}
}

func publicKeyHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/plain")
	keyStr, _ := json.Marshal(publicKey)
	fmt.Fprintln(w, keyStr)
	fmt.Println("Responding to: /get-public-key")
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
	go httpHandler()
	setLocalVariables()
	// go handleTransactions()
	trade()
}
