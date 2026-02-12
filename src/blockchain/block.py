from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
import json
from typing import List, Optional
from src.blockchain.transaction import Transaction

@dataclass
class BlockHeader:
    """Block header containing metadata for the block."""
    previous_hash: str
    merkle_root: str
    difficulty: int
    version: int = 1
    timestamp: float = field(default_factory=datetime.now().timestamp)
    nonce: int = 0

    def calculate_hash(self) -> str:
        """Calculate the block hash from header fields."""
        header_data = {
            'version': self.version,
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'timestamp': self.timestamp,
            'difficulty': self.difficulty,
            'nonce': self.nonce
        }
        return sha256(json.dumps(header_data, sort_keys=True).encode()).hexdigest()

class Block:
    """A block containing transactions in the blockchain."""
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str, difficulty: int = 2):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.timestamp = datetime.now().timestamp()
        self.merkle_root = self.calculate_merkle_root()
        self.nonce = 0
        self.header = BlockHeader(
            previous_hash=previous_hash,
            merkle_root=self.merkle_root,
            difficulty=difficulty
        )
        self.hash = self.calculate_hash()

    def calculate_merkle_root(self) -> str:
        """Calculate the Merkle root of all transactions in the block."""
        if not self.transactions:
            return sha256().hexdigest()
        
        # Start with the transaction hashes
        hashes = [tx.txid for tx in self.transactions]
        
        # If there's an odd number of hashes, duplicate the last one
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])
            
        # Keep hashing pairs until we have a single hash
        while len(hashes) > 1:
            new_hashes = []
            for i in range(0, len(hashes), 2):
                # Combine two hashes and hash them
                combined = hashes[i] + hashes[i+1]
                new_hash = sha256(combined.encode()).hexdigest()
                new_hashes.append(new_hash)
            hashes = new_hashes
            
            # If odd number of hashes, duplicate the last one
            if len(hashes) > 1 and len(hashes) % 2 != 0:
                hashes.append(hashes[-1])
                
        return hashes[0] if hashes else ""

    def calculate_hash(self) -> str:
        """Calculate the block's hash using its header."""
        return self.header.calculate_hash()

    def mine(self) -> None:
        """Mine the block by finding a nonce that satisfies the difficulty target.
        
        PoW serves as a rate limiter, not a source of randomness. It ensures that
        blocks are not created too quickly, making it computationally expensive to
        rewrite transaction history. The difficulty target is adjusted to maintain
        a consistent block time despite changes in network hashrate.
        """
        target = '0' * self.difficulty
        while self.hash[:self.difficulty] != target:
            self.nonce += 1
            self.header.nonce = self.nonce
            self.hash = self.calculate_hash()

    def validate(self, previous_hash: str) -> bool:
        """Validate the block's structure and PoW."""
        # Check previous hash matches
        if self.previous_hash != previous_hash:
            return False
            
        # Check proof of work
        if self.hash[:self.difficulty] != '0' * self.difficulty:
            return False
            
        # Verify merkle root
        if self.calculate_merkle_root() != self.merkle_root:
            return False
            
        return True
