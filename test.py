from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import hashlib, binascii

private_key = rsa.generate_private_key(
    public_exponent=65537,  # Commonly used value for the public exponent
    key_size=2048  # Size of the key in bits
)

public_key = private_key.public_key()

pem_private = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

# Serialize the public key to PEM format
pem_public = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)


data_dict = {"key1": "value1", "key2": "value2"}

# Serialize the dictionary
hash = hashlib.sha256(str(data_dict).encode('UTF-8')).digest()
hash = binascii.hexlify(hash).decode('utf-8')

# Sign the serialized data using the private key
signature = private_key.sign(
    str(hash).encode('UTF-8'),
    padding.PKCS1v15(),
    hashes.SHA256()
)
sig = binascii.hexlify(signature).decode('utf-8')
pub = binascii.hexlify(pem_public).decode('utf-8')

print(sig)
print("")
print(hash)
print("")
print(pub)
# Verify the signature using the public key
try:
    public_key.verify(
        binascii.unhexlify(sig),
        str(hash).encode('UTF-8'), #str(hash).encode('UTF-8') working
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    print("Signature is valid.")
except Exception as e:
    print("Signature is not valid:", e)


sign_hex = "2fc8ff5146fe57d7bfc9f7b9af486737711ad907be9f27bc21d8a4f16cee4b6239fca993121e44d7c67de34a421d43cb1f981bd69ecd3d0c3e30233524094ddfd7e82aae69371c0660f4b978dfbdd1846b41993943e82dc2079758d8c33363bfc8b8004e397d4f8bc51735b2705c4f98c51fb7013c3d06372123067006c75e2aa214d139b19fa463bd362f78f7eab273177b8ad94a03c7a5a8aad14989238d4320a197d6bc241bb18a54c00260b6efb4b1269b5eace38327f806f380980080840fe1fe72388a3e8dc144ec275894ec30d0a199cf12c3495d92317a7a6f8c8bffb3e2798733f43cdc9a0796838692d1e0f14bc9d42b01e503f79720a52302ee2e"
hash_hex = "9e1d4d1f29867c0e59604a8f2d150d9d683cac10297e22343de2d364c1c7cee5"
pem_public_key = "2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d494942496a414e42676b71686b6947397730424151454641414f43415138414d49494243674b43415145416c4a67527131507446487059494146775459646d0a355048674c6252506868757278506f58456c6b6456636f5652366c595a69477377566866362b5731736d67746352666e6a5251547a4e3867646b2f4545456a4d0a3673514c4f644f367a3535715243396e6d2f4f4b6774507a7836746c746559785857464a504f4532442b6c466657505652427576796e7a582f654e4a525461730a77717a6963302f4b4b375138672b615933574a325a30357336494f6f644f766e4c4b74717652564263463750556458536243504b504a4a51517a4f33486a6f350a582b6b34435843515a6866662f4463306b304a66574658613542586a3532432b4e346a352b465456306270393362704d5363374c53783067685a4c4c334e68490a5834484731636d467357646d6b4a2f624f4d777239346971382b4c4f5a732f6851335472336365597a4c336550584154456872574a727469466c3441574151370a55774944415141420a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d0a"

# Convert hexadecimal strings to bytes
signature = bytes.fromhex(sign_hex)
pem_public_key_bytes = bytes.fromhex(pem_public_key)

# Load PEM public key
public_key = load_pem_public_key(pem_public_key_bytes)

# Verify the signature
try:
    public_key.verify(signature, str(hash_hex).encode('UTF-8'), padding.PKCS1v15(), hashes.SHA256())
    print("Signature verification successful")
except Exception as e:
    print("Signature verification failed:", e)