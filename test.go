package main

import (
	"encoding/json"
	"fmt"
	"net"
	"os"
	"time"
)

func broadcastNode(node string) {
	multicastAddr := "192.168.13.255:5006"
	// port := 500

	// Create a UDP address
	udpAddr, err := net.ResolveUDPAddr("udp", multicastAddr)
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
	// fmt.Println("Sending block: ")
	// fmt.Println(blockStr)
	_, err = conn.Write(blockStr)
	fmt.Println("send " + string(blockStr))
	if err != nil {
		fmt.Println("Error sending data:", err)
		os.Exit(1)
	}
}

// func handleTransactions() {
// 	multicastAddr := "239.192.168.10:5007"

// 	addr, _ := net.ResolveUDPAddr("udp", multicastAddr)
// 	conn, _ := net.ListenMulticastUDP("udp", nil, addr)
// 	defer conn.Close()

// 	buffer := make([]byte, 1024)

// 	fmt.Println("Listening for multicast transactions on", multicastAddr)

// 	// Infinite loop to listen for multicast messages
// 	for {
// 		n, _, err := conn.ReadFromUDP(buffer)
// 		if err != nil {
// 			fmt.Println("Error reading from UDP connection:", err)
// 			continue
// 		}

// 		var transaction string
// 		json.Unmarshal(buffer[:n], &transaction)
// 		fmt.Println("rec " + transaction)
// 	}
// }

type Transaction struct {
	Sender   string
	Reciever string
}

func main() {
	// go handleTransactions()
	for i := 0; i < 30; i++ {
		time.Sleep(time.Duration(1) * time.Second)
		broadcastNode("aaab")
	}
	// var transactions = make(map[Transaction]struct{})
	// var t1 = Transaction{}
	// t1.Sender = "aa"
	// var t2 = Transaction{}
	// t2.Sender = "bb"
	// var t3 = Transaction{}
	// t3.Sender = "dd"
	// var t4 = Transaction{}
	// t4.Sender = "ee"

	// transactions[t1] = struct{}{}
	// transactions[t2] = struct{}{}
	// transactions[t3] = struct{}{}
	// transactions[t4] = struct{}{}

	// fmt.Println(transactions)
	// fmt.Println(transactions[1])
}
