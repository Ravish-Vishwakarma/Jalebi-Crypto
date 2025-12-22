import hashlib

i1 = "Hello"

# SHA256 works only on bytes not directly on Python Strings
print(hashlib.sha256(i1.encode()).hexdigest())
# encode() -> b'Hello'
# sha256() -> 32 bit encoding
# hexdigest() -> convert 32 bit to 64 bit
