from typing import Dict, List, Optional, Tuple
from .transaction import Transaction, TransactionOutput, TransactionInput

class UTXOSet:
    """Manages the set of unspent transaction outputs (UTXOs)."""
    
    def __init__(self):
        # Maps (txid, output_index) to TransactionOutput
        self.utxos: Dict[Tuple[str, int], TransactionOutput] = {}
        
    def add_utxo(self, txid: str, output_index: int, output: TransactionOutput) -> None:
        """Add a new UTXO to the set."""
        self.utxos[(txid, output_index)] = output
        
    def remove_utxo(self, txid: str, output_index: int) -> None:
        """Remove a spent UTXO from the set."""
        self.utxos.pop((txid, output_index), None)
        
    def get_utxo(self, txid: str, output_index: int) -> Optional[TransactionOutput]:
        """Get a specific UTXO if it exists and is unspent."""
        return self.utxos.get((txid, output_index))
    
    def get_balance(self, address: str) -> int:
        """Calculate the balance for a given address by summing relevant UTXOs."""
        return sum(
            output.value 
            for output in self.utxos.values() 
            if output.recipient == address
        )
    
    def validate_transaction(self, tx: Transaction) -> Tuple[bool, int]:
        """Validate a transaction against the current UTXO set.
        
        Returns:
            Tuple of (is_valid, total_input_value)
        """
        if tx.is_coinbase():
            return True, 0  # Coinbase has no inputs to validate
            
        total_input = 0
        seen_inputs = set()
        
        for tx_input in tx.inputs:
            # Check for double spend within the same transaction
            input_key = (tx_input.txid, tx_input.output_index)
            if input_key in seen_inputs:
                return False, 0
            seen_inputs.add(input_key)
            
            # Check if input exists and is unspent
            utxo = self.get_utxo(tx_input.txid, tx_input.output_index)
            if not utxo:
                return False, 0
                
            # In a real implementation, verify the signature here
            # For now, we'll assume the signature is valid if the UTXO exists
            
            total_input += utxo.value
            
        total_output = sum(output.value for output in tx.outputs)
        
        # Check that inputs cover outputs (including fees)
        if total_input < total_output:
            return False, 0
            
        return True, total_input
    
    def apply_transaction(self, tx: Transaction) -> None:
        """Apply a valid transaction to the UTXO set."""
        # Remove spent outputs
        for tx_input in tx.inputs:
            self.remove_utxo(tx_input.txid, tx_input.output_index)
            
        # Add new outputs
        for i, output in enumerate(tx.outputs):
            self.add_utxo(tx.txid, i, output)
    
    def apply_block(self, block: 'Block') -> None:
        """Apply all transactions in a block to the UTXO set."""
        for tx in block.transactions:
            self.apply_transaction(tx)
    
    def get_utxos_for_address(self, address: str) -> List[Tuple[str, int, TransactionOutput]]:
        """Get all UTXOs for a specific address."""
        return [
            (txid, idx, output)
            for (txid, idx), output in self.utxos.items()
            if output.recipient == address
        ]
