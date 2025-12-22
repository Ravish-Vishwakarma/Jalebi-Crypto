# -------------------------------------------- WALLET -------------------------------------------- #
import os
import json
import hashlib
import time
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
## Utilities

def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()

def ripemd160(b: bytes) -> bytes:
    h = hashlib.new("ripemd160")
    h.update(b)
    return h.digest()

# Generate Random Keypairs (private key + public key)
def generate_keypair() -> tuple:
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.verifying_key
    return sk.to_string().hex(), vk.to_string().hex()

def pubkey_to_address(pubkey_hex: str) -> str:

    pub_b = bytes.fromhex(pubkey_hex)
    h = ripemd160(sha256(pub_b))
    return h.hex()

#  Transaction signing 
def serialize_tx(tx: dict) -> bytes:

    tx_copy = {k: v for k, v in tx.items() if k not in ("signature", "pubkey")}
    return json.dumps(tx_copy, sort_keys=True, separators=(",", ":")).encode()

def sign_transaction(privkey_hex: str, tx: dict) -> str:

    sk = SigningKey.from_string(bytes.fromhex(privkey_hex), curve=SECP256k1)
    payload = serialize_tx(tx)
    sig = sk.sign(payload)            # bytes
    return sig.hex()

def verify_transaction_signature(pubkey_hex: str, tx: dict, sig_hex: str) -> bool:

    try:
        vk = VerifyingKey.from_string(bytes.fromhex(pubkey_hex), curve=SECP256k1)
        payload = serialize_tx(tx)
        vk.verify(bytes.fromhex(sig_hex), payload)
        return True
    except (BadSignatureError, ValueError):
        return False

#  Convenience: create signed tx 
def create_signed_transaction(privkey_hex: str, pubkey_hex: str, sender_addr: str, recipient_addr: str, amount: int) -> dict:

    tx = {
        "sender": sender_addr,
        "recipient": recipient_addr,
        "amount": amount,
        "timestamp": int(time.time())
    }
    sig = sign_transaction(privkey_hex, tx)
    tx["signature"] = sig
    tx["pubkey"] = pubkey_hex
    return tx
