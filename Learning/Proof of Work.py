import hashlib
import time


class Block:
    def __init__(self, index, previous_hash, data):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = None
    
    def compute_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine(self, difficulty):
        # Target: hash must start with 'difficulty' zeros
        
        target = "0" * difficulty
        while True:
            self.hash = self.compute_hash()
            if self.hash.startswith(target):
                break
            self.nonce += 1
        

# Example mining
block = Block(1, "0", "Some transactions")

start = time.time()
block.mine(difficulty=5)
end = time.time()
print("Block mined!")
print("Nonce:", block.nonce)
print("Hash:", block.hash)
print(f"Time Taken: {round(end-start,3)}s")
