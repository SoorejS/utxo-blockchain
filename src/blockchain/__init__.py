# This file makes Python treat the directory as a package

# Import key classes to make them available at the package level
from .block import Block, BlockHeader
from .transaction import Transaction, TransactionInput, TransactionOutput
from .utxo import UTXOSet
from .blockchain import Blockchain

__all__ = [
    'Block',
    'BlockHeader',
    'Transaction',
    'TransactionInput',
    'TransactionOutput',
    'UTXOSet',
    'Blockchain'
]
