// package main

// import (
// 	"fmt"
// 	"net/http"
// 	"time"
// )

// func printNumbers(stop chan struct{}) {
// 	for i := 0; i <= 100; i++ {
// 		select {
// 		case <-stop:
// 			return
// 		default:
// 			fmt.Println(i)
// 			time.Sleep(time.Millisecond * 100) // Simulating some work
// 		}
// 	}
// }

// func main() {
// 	stop := make(chan struct{})

// 	// Start printing numbers in a goroutine
// 	go printNumbers(stop)

// 	// Set up an HTTP endpoint to stop the printing
// 	http.HandleFunc("/stop", func(w http.ResponseWriter, r *http.Request) {
// 		close(stop)
// 		fmt.Println("Printing stopped.")
// 	})

// 	// Start the HTTP server
// 	fmt.Println("Listening on :8080")
// 	http.ListenAndServe(":8080", nil)
// }

package main

import (
	"bytes"
	"fmt"
	"strings"
)

type Node struct {
	Value    int
	Children []*Node
}

func NewNode(value int) *Node {
	return &Node{Value: value}
}

func (n *Node) AddChild(child *Node) {
	n.Children = append(n.Children, child)
}

func (n *Node) Print(lvl int) {
	fmt.Print(strings.Repeat(" ", lvl))
	fmt.Println(n.Value)
	for _, child := range n.Children {
		fmt.Print(strings.Repeat(" ", lvl))
		child.Print(lvl + 2)
	}
}

func main() {
	// Create a simple chain-like structure with branching
	root := NewNode(1)
	child1 := NewNode(2)
	child2 := NewNode(3)
	root.AddChild(child1)
	root.AddChild(child2)
	child1.AddChild(NewNode(4))
	child1.AddChild(NewNode(5))
	child2.AddChild(NewNode(6))

	// Print the structure
	root.Print(0)

	slice1 := []byte{1, 2, 3, 4, 5}
	slice2 := []byte{1, 2, 3, 4, 5}
	slice3 := []byte{5, 4, 3, 2, 1}
	slice4 := []byte{}

	fmt.Println(bytes.Equal(slice1, slice2)) // true
	fmt.Println(bytes.Equal(slice1, slice3)) // false
	fmt.Println(bytes.Equal(slice1, slice4)) // false
	fmt.Println(bytes.Equal(slice4, slice4)) // true
}
