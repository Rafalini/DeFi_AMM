package main

import (
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"io/ioutil"
)

func loadPrivateKeyFromFile(filePath string) (*rsa.PrivateKey, error) {
	keyBytes, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	block, _ := pem.Decode(keyBytes)
	if block == nil {
		return nil, fmt.Errorf("failed to decode PEM block containing private key")
	}

	key, err := x509.ParsePKCS1PrivateKey(block.Bytes)
	if err != nil {
		key, err = x509.ParsePKCS8PrivateKey(block.Bytes)
		if err != nil {
			return nil, err
		}
		privateKey, ok := key.(*rsa.PrivateKey)
		if !ok {
			return nil, fmt.Errorf("failed to parse private key")
		}
		return privateKey, nil
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
	// Load the signature from the file
	signatureHex, _ := ioutil.ReadFile("signature.txt")
	// publicKeyBytes, _ := ioutil.ReadFile("public_key.pem")
	// privKeyBytes, _ := ioutil.ReadFile("private_key.pem")
	hash, _ := ioutil.ReadFile("hash.txt")
	data, _ := ioutil.ReadFile("data.txt")

	privKey, _ := loadPrivateKeyFromFile("private_key.pem")
	pubKey, _ := loadPublicKeyFromFile("public_key.pem")

	fmt.Printf("%s", privKey)
	fmt.Printf("%s", pubKey)
	fmt.Printf("%s", signatureHex)
	fmt.Printf("%s", hash)
	fmt.Printf("%s", data)
	// Convert signature from hexadecimal string to bytes
	// signature, _ := hex.DecodeString(string(signatureHex))

	// // Load the public key from the file

	// // Parse the public key
	// publicKey, err := parseRSAPublicKeyFromPEM(publicKeyBytes)
	// if err != nil {
	// 	fmt.Println("Error parsing public key:", err)
	// 	return
	// }

	// // Load the data to be verified (hash of the original data in this case)
	// dataToVerify, err := ioutil.ReadFile("hash.txt")
	// if err != nil {
	// 	fmt.Println("Error reading hashed data file:", err)
	// 	return
	// }

	// // Verify the signature against the hashed data using the public key
	// err = rsa.VerifyPKCS1v15(publicKey, crypto.SHA256, dataToVerify, signature)
	// if err != nil {
	// 	fmt.Println("Signature verification failed:", err)
	// 	return
	// }

	// fmt.Println("Signature verified successfully!")
}

// Function to parse RSA public key from PEM format
func parseRSAPublicKeyFromPEM(pubKey []byte) (*rsa.PublicKey, error) {
	pubKeyBlock, _ := pem.Decode(pubKey)
	if pubKeyBlock == nil {
		return nil, fmt.Errorf("failed to parse PEM block containing the public key")
	}

	publicKey, err := x509.ParsePKIXPublicKey(pubKeyBlock.Bytes)
	if err != nil {
		return nil, err
	}

	rsaPubKey, ok := publicKey.(*rsa.PublicKey)
	if !ok {
		return nil, fmt.Errorf("parsed public key is not RSA")
	}

	return rsaPubKey, nil
}
