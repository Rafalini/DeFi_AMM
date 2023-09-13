package main

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"log"
	"main/blockchain"
	"main/metrics"
	"math/rand"
	"net"
	"os"
	"strings"
	"sync"
)

var (
	miner               string
	metricsFile         string
	blockChainFile      string
	localAddr           string
	root                blockchain.TreeNode
	rootLock            sync.Mutex
	miningLock          sync.Mutex
	queueLock           sync.Mutex
	breakHashSearch     = true
	pendingTransactions []blockchain.Transaction
)

const (
	BlockType       string = "block"
	TransactionType        = "transaction"
)

func setLocalVariables() {
	conn, err := net.Dial("udp", "8.8.8.8:80")
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()

	localAddr = conn.LocalAddr().(*net.UDPAddr).String()
	miner, _ = os.Hostname()
	metricsFile = strings.Split(localAddr, ":")[0] + os.Getenv("METRICS_FILE")
	blockChainFile = strings.Split(localAddr, ":")[0] + os.Getenv("BLOCK_CHAIN_FILE")
	root = *blockchain.NewRoot()
}

func printBlock(block blockchain.Block) {
	fmt.Println("Block:")
	for i, s := range block.Transactions {
		fmt.Println(i, s)
	}
	// fmt.Println(block.Nonce)
	// fmt.Printf("%08b\n ", block.Hash)
	printHash(block.Hash)
}

func printHash(hash []byte) {
	// for i, v := range hash {
	// 	fmt.Printf("%08b ", v)
	// 	if i > 4 {
	// 		// break
	// 	}
	// }
	fmt.Println(fmt.Sprintf("%x", hash))
	// fmt.Println("")
}

func searchHash() {
	if len(pendingTransactions) < 3 {
		return
	}

	block := blockchain.Block{}
	block.Miner = localAddr
	block.PreviousHash = blockchain.GetDeepestLeave(&root).Block.Hash

	queueLock.Lock()
	block.Transactions = pendingTransactions[:3]
	pendingTransactions = pendingTransactions[3:]
	queueLock.Unlock()

	h := sha256.New()
	var notFound = true
	block.Nonce = rand.Intn(10000)
	var initialVal = block.Nonce
	for notFound {
		h.Reset()
		blockStr := fmt.Sprintf("%#v", block)
		h.Write([]byte(blockStr))
		block.Hash = h.Sum(nil)

		if block.Hash[0]&0xFF == 0 {
			// fmt.Printf("After %d trials\n", block.Nonce-initialVal)
			notFound = false
		} else {
			block.Nonce += 1
		}

	}

	var stats metrics.Stats
	stats.Attempts = block.Nonce - initialVal
	stats.Times = 1
	metrics.UpdateStats(stats, metricsFile)
	metrics.SaveBlockChain(&root, blockChainFile)

	// printBlock(block)

	rootLock.Lock()
	// blockchain.AppendBlock(&root, &block)
	fmt.Println("Found:")
	fmt.Printf("prev hash: %s\n", fmt.Sprintf("%x", block.PreviousHash))
	fmt.Printf("curr hash: %s\n", fmt.Sprintf("%x", block.Hash))

	rootLock.Unlock()
	broadcastNode(block)
}

func broadcastNode(node blockchain.Block) {
	broadcastAddress := "239.192.168.10"
	port := 5006

	// Create a UDP address
	udpAddr, err := net.ResolveUDPAddr("udp", fmt.Sprintf("%s:%d", broadcastAddress, port))
	if err != nil {
		fmt.Println("Error resolving UDP address:", err)
		os.Exit(1)
	}

	// Create a UDP connection
	conn, err := net.DialUDP("udp", nil, udpAddr)
	if err != nil {
		fmt.Println("Error creating UDP connection:", err)
		os.Exit(1)
	}
	defer conn.Close()

	blockStr, _ := json.Marshal(node)

	_, err = conn.Write(blockStr)
	if err != nil {
		fmt.Println("Error sending data:", err)
		os.Exit(1)
	}
}

func handleTransactions() {
	multicastAddr := "239.192.168.10:5007"

	addr, _ := net.ResolveUDPAddr("udp", multicastAddr)
	conn, _ := net.ListenMulticastUDP("udp", nil, addr)
	defer conn.Close()

	buffer := make([]byte, 1024)

	fmt.Println("Listening for multicast transactions on", multicastAddr)

	// Infinite loop to listen for multicast messages
	for {
		n, _, err := conn.ReadFromUDP(buffer)
		if err != nil {
			fmt.Println("Error reading from UDP connection:", err)
			continue
		}

		var transaction = blockchain.Transaction{}
		json.Unmarshal(buffer[:n], &transaction)
		// fmt.Println(transaction)
		// fmt.Printf("Got Trans: %d\n", n)
		queueLock.Lock()
		pendingTransactions = append(pendingTransactions, transaction)
		queueLock.Unlock()

		searchHash()
	}
}

func handleBlocks() {
	multicastAddr := "239.192.168.10:5006"

	addr, _ := net.ResolveUDPAddr("udp", multicastAddr)
	conn, _ := net.ListenMulticastUDP("udp", nil, addr)
	defer conn.Close()

	buffer := make([]byte, 1024)

	fmt.Println("Listening for multicast blocks on", multicastAddr)

	// Infinite loop to listen for multicast messages
	for {
		n, _, err := conn.ReadFromUDP(buffer)
		if err != nil {
			fmt.Println("Error reading from UDP connection:", err)
			continue
		}

		var block = blockchain.Block{}
		json.Unmarshal(buffer[:n], &block)

		fmt.Println("Recieved:")
		fmt.Printf("prev hash: %s\n", fmt.Sprintf("%x", block.PreviousHash))
		fmt.Printf("curr hash: %s\n", fmt.Sprintf("%x", block.Hash))

		rootLock.Lock()
		blockchain.AppendBlock(&root, &block)
		rootLock.Unlock()

		//break search
	}
}

func main() {
	setLocalVariables()
	go handleTransactions()
	handleBlocks()
}