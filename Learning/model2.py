import hashlib
import time
import json

class JalebiBlock:
    def __init__(self, index, transactions, previous_hash, target):
        """
        BLOCK STRUCTURE EXPLANATION:
        
        1. INDEX: Position of block in chain (0 for genesis, 1, 2, 3...)
        2. TIMESTAMP: When the block was created
        3. TRANSACTIONS: List of all transactions in this block
        4. MERKLE_ROOT: Single hash representing all transactions
        5. PREVIOUS_HASH: Hash of the previous block (creates the "chain")
        6. TARGET: Mining difficulty (number of leading zeros required)
        7. NONCE: Number used once - adjusted during mining
        8. BLOCKHASH: Final hash of this block after mining
        """
        
        # Basic block information
        self.index = index
        self.timestamp = time.time()  # Current time when block is created
        self.transactions = transactions
        
        # Security and integrity
        self.merkle_root_hash = self.merkle_root(transactions)  # Verify all transactions
        self.previous_hash = previous_hash  # Links to previous block
        self.target = target  # Mining difficulty
        
        # Mining results
        self.nonce, self.blockhash = self.mine_block()
        
        print(f"✅ Block {self.index} created with hash: {self.blockhash[:16]}...")

    def compute_block_hash(self, nonce):
        """
        HASH CALCULATION EXPLANATION:
        
        This creates a unique fingerprint for the block by combining:
        - Block index
        - Timestamp  
        - Merkle root of all transactions
        - Previous block's hash
        - Nonce (changed during mining)
        
        SHA-256 ensures any tiny change creates completely different hash
        """
        
        # Combine all block data into one string
        block_string = (
            str(self.index) + 
            str(self.timestamp) + 
            str(self.merkle_root_hash) + 
            str(self.previous_hash) + 
            str(nonce)
        )
        
        # Create SHA-256 hash
        hash_result = hashlib.sha256(block_string.encode()).hexdigest()
        
        # Show what we're hashing (first time only)
        if nonce == 0:
            print(f"🔍 Hashing: {block_string[:50]}...")
            print(f"📋 Hash attempt: {hash_result}")
        
        return hash_result
    
    def is_valid_block(self):
        """
        PROOF OF WORK VALIDATION:
        
        Checks if block hash starts with required number of zeros.
        This is what makes mining computationally expensive!
        
        Example:
        - Target "000" means hash must start with 000xxxxx...
        - Target "0000" means hash must start with 0000xxxx... (harder!)
        """
        is_valid = self.blockhash.startswith(self.target)
        print(f"🎯 Block validation: {'VALID' if is_valid else 'INVALID'}")
        print(f"   Required: {self.target}xxxxxx...")
        print(f"   Got:      {self.blockhash[:len(self.target)]}xxxxxx...")
        return is_valid
    
    def mine_block(self):
        """
        PROOF OF WORK MINING EXPLANATION:
        
        This is the heart of blockchain security!
        
        1. Try different nonce values (0, 1, 2, 3...)
        2. For each nonce, calculate block hash
        3. Check if hash starts with required zeros (target)
        4. If yes: mining complete! If no: try next nonce
        5. This requires computational work, making tampering expensive
        """
        
        print(f"⛏️  Mining Block {self.index} (Target: {self.target})")
        print(f"🎯 Need hash starting with: {self.target}")
        
        nonce = 0
        attempts = 0
        start_time = time.time()
        
        while True:
            attempts += 1
            block_hash = self.compute_block_hash(nonce)
            
            # Show progress every 10000 attempts
            if attempts % 10000 == 0:
                print(f"⏳ Tried {attempts} nonces... Current hash: {block_hash[:16]}...")
            
            # Check if we found valid hash
            if block_hash.startswith(self.target):
                end_time = time.time()
                print(f"💎 SUCCESS! Found valid hash!")
                print(f"📊 Mining Stats:")
                print(f"   - Attempts: {attempts}")
                print(f"   - Nonce: {nonce}")
                print(f"   - Time: {end_time - start_time:.2f} seconds")
                print(f"   - Hash: {block_hash}")
                return nonce, block_hash

            nonce += 1
    
    def hash_data(self, data):
        """
        UTILITY FUNCTION:
        Simple helper to hash any data consistently
        """
        return hashlib.sha256(str(data).encode()).hexdigest()

    def merkle_root(self, transactions):
        """
        MERKLE TREE EXPLANATION:
        
        A Merkle tree creates a single hash representing ALL transactions.
        This allows quick verification that transactions haven't been tampered with.
        
        Process:
        1. Hash each transaction individually
        2. Pair up hashes and hash the pairs
        3. Repeat until only one hash remains
        4. That's the Merkle root!
        
        Example with 4 transactions:
        TX1  TX2  TX3  TX4
         |    |    |    |
        H1   H2   H3   H4
         \   /     \   /
          H12       H34
            \       /
             ROOT
        """
        
        if not transactions:
            print("📝 No transactions - using empty hash")
            return "0" * 64
        
        print(f"🌳 Building Merkle tree for {len(transactions)} transactions")
        
        # Step 1: Hash all transactions
        layer = [self.hash_data(json.dumps(tx, sort_keys=True)) for tx in transactions]
        print(f"🔹 Layer 0 (Transaction hashes): {len(layer)} hashes")
        
        layer_num = 1
        while len(layer) > 1:
            new_layer = []
            print(f"🔹 Layer {layer_num}: Processing {len(layer)} hashes")
            
            for i in range(0, len(layer), 2):
                left = layer[i]
                # If odd number of hashes, duplicate the last one
                right = layer[i + 1] if (i + 1) < len(layer) else left
                
                combined_hash = self.hash_data(left + right)
                new_layer.append(combined_hash)
                print(f"   {left[:8]}... + {right[:8]}... = {combined_hash[:8]}...")
            
            layer = new_layer
            layer_num += 1

        merkle_root = layer[0]
        print(f"🎯 Merkle Root: {merkle_root}")
        return merkle_root

# Let's test this step by step!
print("🥨 JALEBI BLOCKCHAIN - BLOCK CONCEPTS")
print("=" * 50)

# Create some sample transactions
sample_transactions = [
    {"sender": "Alice", "recipient": "Bob", "amount": 10},
    {"sender": "Bob", "recipient": "Charlie", "amount": 5},
    {"sender": "Charlie", "recipient": "Alice", "amount": 3}
]

print(f"\n📦 Creating block with {len(sample_transactions)} transactions...")
print("Transactions:")
for i, tx in enumerate(sample_transactions):
    print(f"  {i+1}. {tx['sender']} → {tx['recipient']}: {tx['amount']}")

# Create a block (this will show all the mining process)
test_block = JalebiBlock(
    index=1,
    transactions=sample_transactions,
    previous_hash="0" * 64,  # Fake previous hash for demo
    target="00"  # Easier target for demo (2 zeros)
)

print(f"\n📋 FINAL BLOCK SUMMARY:")
print(f"Index: {test_block.index}")
print(f"Timestamp: {test_block.timestamp}")
print(f"Transactions: {len(test_block.transactions)}")
print(f"Merkle Root: {test_block.merkle_root_hash[:16]}...")
print(f"Previous Hash: {test_block.previous_hash[:16]}...")
print(f"Nonce: {test_block.nonce}")
print(f"Block Hash: {test_block.blockhash}")
print(f"Valid: {test_block.is_valid_block()}")