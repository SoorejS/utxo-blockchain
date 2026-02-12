from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import copy
from src.blockchain.block import Block
from src.blockchain.transaction import Transaction, TransactionInput, TransactionOutput
from src.blockchain.utxo import UTXOSet

class Blockchain:
    """
    A simplified blockchain implementation with UTXO model and fork resolution.
    """
    
    def __init__(self, difficulty: int = 2):
        self.difficulty = difficulty
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.utxo = UTXOSet()
        self.forks: List[List[Block]] = []  # Alternative chains
        self.create_genesis_block()
    
    def create_genesis_block(self) -> None:
        """Create the genesis block (first block in the chain)."""
        genesis_block = Block(
            index=0,
            transactions=[],
            previous_hash="0" * 64,  # Hardcoded for genesis
            difficulty=self.difficulty
        )
        genesis_block.mine()
        self.chain.append(genesis_block)
    
    @property
    def last_block(self) -> Block:
        """Get the last block in the current active chain."""
        return self.chain[-1]
    
    def add_transaction(self, tx: Transaction) -> bool:
        """Add a new transaction to the pending transactions pool."""
        is_valid, _ = self.utxo.validate_transaction(tx)
        if is_valid:
            self.pending_transactions.append(tx)
            return True
        return False
    
    def mine_block(self, miner_address: str) -> Optional[Block]:
        """Mine a new block with pending transactions."""
        if not self.pending_transactions:
            return None
        
        # Create coinbase transaction (mining reward)
        coinbase_tx = Transaction(
            inputs=[],
            outputs=[TransactionOutput(value=50, recipient=miner_address)]
        )
        
        # Include pending transactions
        block_transactions = [coinbase_tx] + self.pending_transactions
        
        # Create and mine new block
        new_block = Block(
            index=len(self.chain),
            transactions=block_transactions,
            previous_hash=self.last_block.hash,
            difficulty=self.difficulty
        )
        new_block.mine()
        
        # Validate and add to chain
        if self.add_block(new_block):
            self.pending_transactions = []
            return new_block
        return None
    
    def add_block(self, block: Block) -> bool:
        """Add a new block to the blockchain after validation."""
        # Basic validation
        if not self.is_valid_block(block):
            return False
        
        # Check for forks
        if block.previous_hash != self.last_block.hash:
            return self._handle_fork(block)
        
        # Add to main chain
        self.chain.append(block)
        self.utxo.apply_block(block)
        return True
    
    def _handle_fork(self, block: Block) -> bool:
        """Handle potential forks in the blockchain."""
        # Find the chain this block extends
        for i, fork_chain in enumerate(self.forks):
            if block.previous_hash == fork_chain[-1].hash:
                fork_chain.append(block)
                # Check if this fork is now longer than main chain
                if len(fork_chain) > len(self.chain):
                    self._switch_to_fork(fork_chain, i)
                return True
        
        # If no matching fork found, create a new one
        matching_blocks = [b for b in self.chain if b.hash == block.previous_hash]
        if matching_blocks:
            fork_index = self.chain.index(matching_blocks[0])
            fork_chain = self.chain[:fork_index + 1] + [block]
            self.forks.append(fork_chain)
            return True
            
        return False
    
    def _switch_to_fork(self, fork_chain: List[Block], fork_index: int) -> None:
        """Switch to a longer valid fork."""
        # Revert transactions from current chain
        old_chain = self.chain[len(fork_chain) - 1:]
        self.utxo = UTXOSet()  # Reset UTXO set
        
        # Rebuild UTXO set up to fork point
        for block in self.chain[:len(fork_chain) - 1]:
            self.utxo.apply_block(block)
        
        # Apply all blocks in the fork
        for block in fork_chain[len(self.chain):]:
            self.utxo.apply_block(block)
        
        # Update chain and remove the fork
        self.chain = fork_chain
        self.forks.pop(fork_index)
    
    def is_valid_block(self, block: Block) -> bool:
        """Validate a block and its transactions."""
        # Verify block structure and PoW
        if not block.validate(self.last_block.hash):
            return False
        
        # Create a temporary UTXO set to validate the block
        temp_utxo = copy.deepcopy(self.utxo)
        total_fees = 0
        seen_txids = set()
        
        # Validate each transaction
        for tx in block.transactions:
            # Check for duplicate transactions
            if tx.txid in seen_txids:
                return False
            seen_txids.add(tx.txid)
            
            # Skip coinbase for now
            if tx.is_coinbase():
                continue
                
            is_valid, input_value = temp_utxo.validate_transaction(tx)
            if not is_valid:
                return False
                
            # Calculate and accumulate fees
            output_value = sum(out.value for out in tx.outputs)
            total_fees += (input_value - output_value)
            
            # Apply transaction to temporary UTXO set
            temp_utxo.apply_transaction(tx)
        
        # Verify coinbase transaction (must be first)
        if block.transactions and block.transactions[0].is_coinbase():
            coinbase = block.transactions[0]
            # In a real implementation, the coinbase amount would include fees
            # For simplicity, we're using a fixed reward of 50
            if len(coinbase.outputs) != 1 or coinbase.outputs[0].value != 50:
                return False
        
        return True
    
    def get_balance(self, address: str) -> int:
        """Get the balance for a given address."""
        return self.utxo.get_balance(address)
    
    def get_chain_difficulty(self, chain: Optional[List[Block]] = None) -> int:
        """Calculate the total proof-of-work difficulty of a chain."""
        if chain is None:
            chain = self.chain
        return sum(2 ** block.difficulty for block in chain)
