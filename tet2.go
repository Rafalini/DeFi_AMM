package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

func main() {
	// Example JSON payload
	jsonData := map[string]interface{}{
		"key1": "value1",
		"key2": "value2",
	}

	// Encode JSON data
	jsonBytes, err := json.Marshal(jsonData)
	if err != nil {
		fmt.Println("Error encoding JSON:", err)
		return
	}

	// Create a new request with a JSON body
	req, err := http.NewRequest("GET", "https://your-api-endpoint.com", bytes.NewBuffer(jsonBytes))
	if err != nil {
		fmt.Println("Error creating request:", err)
		return
	}

	// Set headers to indicate JSON content
	req.Header.Set("Content-Type", "application/json")

	// Create an HTTP client
	client := &http.Client{}

	// Send the request
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Error sending request:", err)
		return
	}
	defer resp.Body.Close()

	// Check the response status
	fmt.Println("Response Status:", resp.Status)
}
