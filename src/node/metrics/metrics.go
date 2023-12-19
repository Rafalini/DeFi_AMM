package metrics

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"time"
)

func PrepareLog(fileName string) {
	file, err := os.Create(fileName)
	check(err)
	writer := csv.NewWriter(file)
	err = writer.Write([]string{"Timestamp", "USDvalue"})
	check(err)
	defer writer.Flush()
}

func UpdateLog(balances map[string]float64, prices map[string]float64, fileName string) {

	_, err := os.Stat(fileName)
	check(err)

	sum := 0.0
	for key := range balances {
		sum += balances[key] * prices[key]
	}

	var file *os.File
	file, err = os.OpenFile(fileName, os.O_APPEND|os.O_WRONLY, os.ModeAppend)
	check(err)
	defer file.Close()

	// Create a CSV writer
	writer := csv.NewWriter(file)
	defer writer.Flush()

	// Get current timestamp
	timestamp := time.Now().Format("2006-01-02 15:04:05")

	// Prepare data to write to CSV
	data := []string{timestamp, fmt.Sprintf("%.2f", sum)}

	// Append data to the CSV file
	if err := writer.Write(data); err != nil {
		log.Fatal("Error writing data to CSV:", err)
	}

	// Flush data to ensure it is written immediately
	writer.Flush()
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}
