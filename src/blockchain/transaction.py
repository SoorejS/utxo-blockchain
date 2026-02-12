from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
import json
from typing import List, Dict, Optional

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

class Transaction:
    """A transaction that transfers value from inputs to outputs."""
    def __init__(self, inputs: List[TransactionInput], outputs: List[TransactionOutput]):
        self.inputs = inputs
        self.outputs = outputs
        self.timestamp = datetime.now().timestamp()
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

    def calculate_fee(self, input_values: List[int]) -> int:
        """Calculate transaction fee based on input and output values."""
        total_in = sum(input_values)
        total_out = sum(out.value for out in self.outputs)
        return total_in - total_out
