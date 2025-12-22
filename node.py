from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import time

from main import JalebiBlockchain
from wallet import verify_transaction_signature

# Initialize FastAPI and blockchain
app = FastAPI(title="JalebiChain Node", version="1.0")
blockchain = JalebiBlockchain()

# Pydantic model for transaction validation
class TransactionModel(BaseModel):
    sender: str
    recipient: str
    amount: float
    timestamp: int
    signature: str
    pubkey: str

# ------------------- ROUTES -------------------

@app.get("/")
def root():
    return {"message": "Welcome to JalebiChain Node!"}

@app.get("/chain")
def get_chain():
    return {
        "length": len(blockchain.chain),
        "chain": [
            {
                "index": b.index,
                "timestamp": b.timestamp,
                "transactions": b.transactions,
                "previous_hash": b.previous_hash,
                "blockhash": b.blockhash,
                "merkle_root_hash": b.merkle_root_hash
            } for b in blockchain.chain
        ]
    }

@app.get("/balance/{address}")
def get_balance(address: str):
    balance = blockchain.get_balance(address)
    return {"address": address, "balance": balance}

@app.post("/transaction/new")
def add_transaction(tx: TransactionModel):
    tx_data = tx.dict()
    # Verify signature
    if not verify_transaction_signature(tx_data["pubkey"], tx_data, tx_data["signature"]):
        raise HTTPException(status_code=400, detail="Invalid transaction signature")

    # Add to mempool
    success = blockchain.add_transaction(tx_data)
    if not success:
        raise HTTPException(status_code=400, detail="Transaction rejected")

    return {"message": "Transaction added to mempool", "mempool_size": len(blockchain.mempool)}

@app.get("/mine")
def mine_block():
    if not blockchain.mempool:
        raise HTTPException(status_code=400, detail="No pending transactions to mine")

    block = blockchain.mine_pending_transactions()
    return {
        "message": "Block mined successfully",
        "index": block.index,
        "hash": block.blockhash,
        "transactions": block.transactions
    }

@app.get("/valid")
def validate_chain():
    valid = blockchain.is_chain_valid()
    return {"is_valid": valid}
