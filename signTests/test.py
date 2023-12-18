from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import hashlib
import json
import binascii

# Generate an RSA private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Get the public key
public_key = private_key.public_key()

# Serialize and save the private key to a file
with open('private_key.pem', 'wb') as private_key_file:
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    private_key_file.write(private_key_pem)

# Serialize and save the public key to a file
with open('public_key.pem', 'wb') as public_key_file:
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public_key_file.write(public_key_pem)

# Create a sample dictionary to sign
with open('data.txt', 'r') as private_key_file:
    data_to_sign = private_key_file.read()
print(data_to_sign)
# Convert the dictionary to bytes
json_data = json.dumps(data_to_sign).encode()

# Hash the data
# hash_algorithm = hashlib.sha256()
# hash_algorithm.update(json_data)
# hashed_data = hash_algorithm.digest()

# Sign the hashed data using the private key
signature = private_key.sign(
    json_data,
    padding.PKCS1v15(),
    hashes.SHA256()
)

with open('hash.txt', 'w') as public_key_file:
    public_key_file.write(binascii.hexlify(json_data).decode())
# Convert the signature to hexadecimal string
hex_signature = binascii.hexlify(signature).decode()

# Save the signature to a file
with open('signature.txt', 'w') as signature_file:
    signature_file.write(hex_signature)
