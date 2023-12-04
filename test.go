package main

import (
	"crypto"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"os"
)

func main() {
	// Generate a private/public key pair
	privateKey, publicKey := generateKeyPairAndReturn()

	// Your data/message to be signed
	message := []byte("Hello, this is a message to be signed")
	// Create a new SHA256 hash

	signature := sign(privateKey, message)
	// Verify the signature using the public key
	err := rsa.VerifyPKCS1v15(&publicKey, crypto.SHA256, returnHash(message), signature)
	if err != nil {
		fmt.Println("Signature verification failed:", err)
		return
	}

	fmt.Println("Signature verified successfully!")
}

func returnHash(message []byte) []byte {
	hash := sha256.New()
	hash.Write(message)
	return hash.Sum(nil)
}

func sign(privateKey *rsa.PrivateKey, message []byte) []byte {
	signature, _ := rsa.SignPKCS1v15(rand.Reader, privateKey, crypto.SHA256, returnHash(message))
	return signature
}

func generateKeyPairAndReturn() (*rsa.PrivateKey, rsa.PublicKey) {
	// Generate a new RSA key pair with a key size of 2048 bits
	privateKey, _ := rsa.GenerateKey(rand.Reader, 2048)

	// Encode the private key to ASN.1 DER format
	privateKeyBytes := x509.MarshalPKCS1PrivateKey(privateKey)

	// Create a PEM block for the private key
	privateKeyPEM := &pem.Block{
		Type:  "RSA PRIVATE KEY",
		Bytes: privateKeyBytes,
	}

	// Write the private key to a file
	privateKeyFile, _ := os.Create("private_key.pem")
	defer privateKeyFile.Close()
	pem.Encode(privateKeyFile, privateKeyPEM)

	// Extract the public key from the private key
	publicKey := privateKey.PublicKey

	// Marshal the public key to ASN.1 DER format
	publicKeyBytes, _ := x509.MarshalPKIXPublicKey(&publicKey)

	// Create a PEM block for the public key
	publicKeyPEM := &pem.Block{
		Type:  "PUBLIC KEY",
		Bytes: publicKeyBytes,
	}

	// Write the public key to a file
	publicKeyFile, _ := os.Create("public_key.pem")
	defer publicKeyFile.Close()

	pem.Encode(publicKeyFile, publicKeyPEM)

	return privateKey, publicKey
}
