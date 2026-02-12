import hashlib
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from hashlib import sha256
import json

@dataclass
class TransactionInput:
    """Represents a transaction input that references an output from a previous transaction."""
    txid: str          # Reference to the transaction containing the output
    output_index: int  # Index of the output in the referenced transaction
    signature: str     # In a real implementation, this would verify ownership

@dataclass
class TransactionOutput:
    """Represents a transaction output that can be spent in a future transaction."""
    value: int         # Amount of coins
    recipient: str     # Public key hash of the recipient

@dataclass
class Transaction:
    """A transaction that transfers value from inputs to outputs."""
    inputs: List[TransactionInput]
    outputs: List[TransactionOutput]
    timestamp: float = field(default_factory=datetime.now().timestamp)
    txid: str = ""

    def __post_init__(self):
        """Calculate the transaction ID after initialization."""
        self.txid = self.calculate_txid()

    def calculate_txid(self) -> str:
        """Calculate the transaction ID using a hash of its contents."""
        tx_data = {
            'inputs': [
                {'txid': inp.txid, 'output_index': inp.output_index, 'signature': inp.signature}
                for inp in self.inputs
            ],
            'outputs': [
                {'value': out.value, 'recipient': out.recipient}
                for out in self.outputs
            ],
            'timestamp': self.timestamp
        }
        return sha256(json.dumps(tx_data, sort_keys=True).encode()).hexdigest()

    def is_coinbase(self) -> bool:
        """Check if this is a coinbase transaction (mining reward)."""
        return not self.inputs

@dataclass
class Block:
    """A block containing transactions in the blockchain."""
    index: int
    transactions: List[Transaction]
    previous_hash: str
    timestamp: float = field(default_factory=datetime.now().timestamp)
    nonce: int = 0
    hash: str = ""

    def __post_init__(self):
        """Calculate the block hash after initialization."""
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate the block's hash using its contents."""
        block_data = {
            'index': self.index,
            'transactions': [tx.txid for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }
        return sha256(json.dumps(block_data, sort_keys=True).encode()).hexdigest()

    def mine(self, difficulty: int):
        """Mine the block by finding a nonce that satisfies the difficulty target."""
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    """A simple blockchain implementation using Proof of Work."""
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.utxos: Dict[str, TransactionOutput] = {}  # Maps txid+output_index to TransactionOutput
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        """Create the first block in the blockchain (genesis block)."""
        genesis_block = Block(
            index=0,
            transactions=[],
            previous_hash="0" * 64,
            timestamp=datetime(2024, 1, 1).timestamp()
        )
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self) -> Block:
        """Get the most recent block in the chain."""
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction) -> bool:
        """Add a new transaction to the pending transactions list."""
        if not self.is_valid_transaction(transaction):
            return False
        
        # Mark UTXOs as spent
        for tx_input in transaction.inputs:
            utxo_key = f"{tx_input.txid}:{tx_input.output_index}"
            if utxo_key in self.utxos:
                del self.utxos[utxo_key]
        
        # Add new UTXOs
        for i, output in enumerate(transaction.outputs):
            utxo_key = f"{transaction.txid}:{i}"
            self.utxos[utxo_key] = output
            
        self.pending_transactions.append(transaction)
        return True

    def is_valid_transaction(self, transaction: Transaction) -> bool:
        """Validate a transaction against the current UTXO set."""
        # Coinbase transactions are always valid
        if transaction.is_coinbase():
            return True
            
        input_sum = 0
        output_sum = sum(output.value for output in transaction.outputs)
        
        # Check all inputs reference unspent outputs and sum their values
        for tx_input in transaction.inputs:
            utxo_key = f"{tx_input.txid}:{tx_input.output_index}"
            
            # Check if UTXO exists and hasn't been spent
            if utxo_key not in self.utxos:
                return False
                
            # In a real implementation, verify the signature here
            # For simplicity, we'll just assume the signature is valid
            
            input_sum += self.utxos[utxo_key].value
        
        # Check that inputs cover outputs (including fees)
        if input_sum < output_sum:
            return False
            
        return True

    def mine_pending_transactions(self, miner_address: str) -> Optional[Block]:
        """Mine pending transactions and add a new block to the chain."""
        if not self.pending_transactions:
            return None

        # Add coinbase transaction (mining reward)
        coinbase_tx = Transaction(
            inputs=[],
            outputs=[TransactionOutput(value=50, recipient=miner_address)]
        )
        self.pending_transactions.insert(0, coinbase_tx)
        
        # Create and mine the new block
        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions.copy(),
            previous_hash=self.last_block.hash
        )
        new_block.mine(self.difficulty)
        
        # Add the new block to the chain
        self.chain.append(new_block)
        
        # Clear pending transactions
        self.pending_transactions = []
        
        return new_block

    def is_chain_valid(self) -> bool:
        """Check if the blockchain is valid."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check block hash is correct
            if current_block.hash != current_block.calculate_hash():
                return False
                
            # Check previous hash reference
            if current_block.previous_hash != previous_block.hash:
                return False
                
            # Check proof of work
            if current_block.hash[:self.difficulty] != '0' * self.difficulty:
                return False
                
        return True

    def get_balance(self, address: str) -> int:
        """Get the balance of an address by summing up all unspent outputs."""
        balance = 0
        for utxo_key, output in self.utxos.items():
            if output.recipient == address:
                balance += output.value
        return balance
