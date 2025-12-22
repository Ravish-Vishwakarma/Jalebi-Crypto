import hashlib
import time
import json
import sqlite3
from ecdsa import SigningKey, VerifyingKey, BadSignatureError, SECP256k1

# -------------------------------------------- DATABASE -------------------------------------------- #
DB_FILE = "jalebi.db"
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Blocks
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blocks (
        height INTEGER PRIMARY KEY,
        hash TEXT,
        prev_hash TEXT,
        timestamp REAL
    )
    """)

    # Transactions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        txid TEXT PRIMARY KEY,
        block_height INTEGER,
        sender TEXT,
        recipient TEXT,
        amount INTEGER
    )
    """)

    # UTXO set
    cur.execute("""
    CREATE TABLE IF NOT EXISTS utxos (
        txid TEXT,
        recipient TEXT,
        amount INTEGER,
        spent INTEGER DEFAULT 0,
        PRIMARY KEY (txid, recipient)
    )
    """)

    conn.commit()
    conn.close()

# -------------------------------------------- Block -------------------------------------------- #
class JalebiBlock:
    def __init__(self, index, transactions, previous_hash, target):
        self.index = index
        self.timestamp= time.time()
        self.transactions= transactions
        self.merkle_root_hash= self.merkle_root(transactions)
        self.previous_hash = previous_hash
        self.target = target
        self.nonce, self.blockhash = self.mine_block()

    def compute_block_hash(self, nonce):
        block_string = (str(self.index)+str(self.timestamp)+str(self.merkle_root_hash)+str(self.previous_hash)+str(nonce))
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def is_valid_block(self):
        return self.blockhash.startswith(self.target)
    
    def mine_block(self):
        print(f"Mining Block {self.index}")
        nonce = 0
        while True:
            block_hash = self.compute_block_hash(nonce)
            if (block_hash.startswith(self.target)):
                return nonce, block_hash

            nonce+=1
    
    def hash_data(self, data):
        return hashlib.sha256(str(data).encode()).hexdigest()

    def merkle_root(self, transactions):
        if not transactions:
            return "0"*64
        
        layer = [self.hash_data(json.dumps(tx, sort_keys=True)) for tx in transactions]
        while len(layer) > 1:
            new_layer = []
            for i in range(0,len(layer),2):
                l = layer[i]
                r = layer[i+1] if (i+1) < len(layer) else l
                new_layer.append(self.hash_data(l+r))
            layer = new_layer

        return layer[0]
    
    def get_merkle_proof(self, transaction):
        tx_hash = self.hash_data(json.dumps(transaction, sort_keys=True))
        layer = [self.hash_data(json.dumps(tx, sort_keys=True)) for tx in self.transactions]

        if tx_hash not in layer:
            return None

        proof = []
        while len(layer) > 1:
            new_layer = []
            for i in range(0, len(layer), 2):
                l = layer[i]
                r = layer[i+1] if i+1 < len(layer) else l

                if tx_hash == l and l != r:
                    proof.append(("right", r))  # sibling is on the right
                    tx_hash = self.hash_data(l + r)
                elif tx_hash == r:
                    proof.append(("left", l))   # sibling is on the left
                    tx_hash = self.hash_data(l + r)

                new_layer.append(self.hash_data(l + r))
            layer = new_layer

        return proof

    @staticmethod
    def verify_merkle_proof(transaction, proof, merkle_root):
        tx_hash = hashlib.sha256(json.dumps(transaction, sort_keys=True).encode()).hexdigest()
        computed = tx_hash

        for direction, sibling in proof:
            if direction == "left":
                computed = hashlib.sha256((sibling + computed).encode()).hexdigest()
            else:
                computed = hashlib.sha256((computed + sibling).encode()).hexdigest()

        return computed == merkle_root






# -------------------------------------------- BlockChain -------------------------------------------- #
class JalebiBlockchain:
    def __init__(self):
        self.chain = [] # Hold our Blocks
        self.mempool = [] # Holds our transactions before validating
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = JalebiBlock(
            0,
            [{"sender": "Genesis", "recipient": "Network", "amount": 0}],
            "0"*64,
            "0"*3
        )
        self.chain.append(genesis_block)

    def get_lastblock(self):
        return self.chain[-1]
    

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx["sender"] == address:
                    balance -= tx["amount"]
                if  tx["recipient"] == address:
                    balance += tx["amount"]
        return balance
    
    def add_transaction(self, tx):
        if self.get_balance(tx["sender"]) < tx["amount"]:
                print("Insufficient balance. Transaction rejected.")
                return False

        if not verify_transaction_signature(tx["pubkey"],tx,tx["signature"]):
            print("Invalid transaction signature, Rejected")
            return False
        self.mempool.append(tx)
        return True

    def mine_pending_transactions(self, miner_address):
        reward_tx = {
            "sender": "Network",
            "recipient": miner_address,
            "amount": 50,  # reward amount
            "timestamp": int(time.time()),
            "signature": "",
            "pubkey": ""
            }
        valid_transactions = [reward_tx]  
        temp_balances = {}

        for tx in self.mempool:
            sender = tx["sender"]
            recipient = tx["recipient"]
            amount = tx["amount"]
        if sender not in temp_balances:
            temp_balances[sender] = self.get_balance(sender)
        if recipient not in temp_balances:
            temp_balances[recipient] = self.get_balance(recipient)


        if temp_balances[sender] >= amount:
            valid_transactions.append(tx)
            temp_balances[sender] -= amount
            temp_balances[recipient] += amount
        else:
            print(f"Rejected double-spend or overspend tx from {sender}")  
        
        block = JalebiBlock(
            len(self.chain),
            self.mempool,
            self.get_lastblock().blockhash,
            "0"*3
        )
        self.chain.append(block)
        self.mempool = []
        return block
    
    def is_chain_valid(self):   
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if(current_block.previous_hash != previous_block.blockhash):
                return False
            
            if not current_block.is_valid_block():
                return False
            
        return True



# -------------------------------------------- END -------------------------------------------- #


from wallet import generate_keypair, pubkey_to_address, sign_transaction, verify_transaction_signature
# create wallet A
priv_a, pub_a = generate_keypair()
addr_a = pubkey_to_address(pub_a)

# create wallet B
priv_b, pub_b = generate_keypair()
addr_b = pubkey_to_address(pub_b)


tx = {"sender": addr_a, "recipient": addr_b, "amount": 10, "timestamp": int(time.time())}


sig = sign_transaction(priv_a, tx)


tx["signature"] = sig
tx["pubkey"] = pub_a


valid = verify_transaction_signature(tx["pubkey"], tx, tx["signature"])
print("Signature valid?", valid) 

# create wallet A
priv_a, pub_a = generate_keypair()
addr_a = pubkey_to_address(pub_a)

# create wallet B
priv_b, pub_b = generate_keypair()
addr_b = pubkey_to_address(pub_b)


tx = {"sender": addr_a, "recipient": addr_b, "amount": 10, "timestamp": int(time.time())}

sig = sign_transaction(priv_a, tx)

tx["signature"] = sig
tx["pubkey"] = pub_a


valid = verify_transaction_signature(tx["pubkey"], tx, tx["signature"])
print("Signature valid?", valid)

