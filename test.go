package main

import (
	"crypto/rand"
	"crypto/rsa"
	"fmt"
)

func main() {
	// Generate RSA key pair
	privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		fmt.Println("Error generating RSA private key:", err)
		return
	}

	// Extract public key from private key
	publicKey := &privateKey.PublicKey

	// Message to be encrypted
	message := []byte("This is a secret message!")

	// Encrypt message using the public key
	encryptedMsg, err := rsa.EncryptPKCS1v15(rand.Reader, publicKey, message)
	if err != nil {
		fmt.Println("Error encrypting message:", err)
		return
	}

	fmt.Println("Encrypted message:", encryptedMsg)

	// Decrypt the encrypted message using the private key
	decryptedMsg, err := rsa.DecryptPKCS1v15(rand.Reader, privateKey, encryptedMsg)
	if err != nil {
		fmt.Println("Error decrypting message:", err)
		return
	}

	fmt.Println("Decrypted message:", string(decryptedMsg))
}
