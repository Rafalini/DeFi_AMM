package main

import (
	"crypto"
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"io/ioutil"
	"os"
)

var (
	privateKey *rsa.PrivateKey
	publicKey  rsa.PublicKey
)

func loadPrivateKeyFromFile(filePath string) (interface{}, error) {
	keyBytes, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	block, _ := pem.Decode(keyBytes)
	if block == nil {
		return nil, fmt.Errorf("failed to decode PEM block containing public key")
	}

	key, err := x509.ParsePKCS8PrivateKey(block.Bytes)
	if err != nil {
		return nil, err
	}

	return key, nil
}

func loadPublicKeyFromFile(filePath string) (interface{}, error) {
	keyBytes, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	block, _ := pem.Decode(keyBytes)
	if block == nil {
		return nil, fmt.Errorf("failed to decode PEM block containing public key")
	}

	key, err := x509.ParsePKIXPublicKey(block.Bytes)
	if err != nil {
		return nil, err
	}

	return key, nil
}

func main() {
	privateKeyPath := "private_key.pem"
	// publicKeyPath := "public_key.pem"

	privateKey, err := loadPrivateKeyFromFile(privateKeyPath)
	if err != nil {
		fmt.Println("Error loading private key:", err)
		os.Exit(1)
	}

	fmt.Println("Private Key Loaded:")

	// publicKey, err := loadPublicKeyFromFile(publicKeyPath)
	// if err != nil {
	// 	fmt.Println("Error loading public key:", err)
	// 	os.Exit(1)
	// }

	fmt.Println("Public Key Loaded:")

	hash, _ := ioutil.ReadFile("hash.txt")
	sig, _ := rsa.SignPKCS1v15(rand.Reader, privateKey, crypto.SHA256, hash)
	err = ioutil.WriteFile("output.txt", []byte(sig), 0644)
}
