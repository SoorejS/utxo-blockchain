# Minimal UTXO Blockchain Implementation

A minimal, educational implementation of a Bitcoin-style blockchain using the Unspent Transaction Output (UTXO) model. This project focuses on correctness and core blockchain concepts rather than performance or production-readiness.

## Core Concepts

### UTXO Model

Unlike account-based models (like Ethereum), this implementation uses the UTXO model where:
- Each transaction consumes existing UTXOs as inputs
- Creates new UTXOs as outputs
- No global account balances are maintained
- Double-spending is prevented by tracking spent outputs

### Block Structure

Each block contains:
- Block header (version, previous hash, Merkle root, timestamp, difficulty, nonce)
- List of transactions
- Proof-of-Work (PoW) validation
- Merkle root for efficient transaction verification

### Key Components

1. **Transaction**
   - Inputs (references to previous outputs)
   - Outputs (new UTXOs)
   - Transaction ID (hash of transaction data)

2. **Block**
   - Header with PoW
   - Merkle tree of transactions
   - Mining functionality

3. **UTXO Set**
   - Tracks all unspent transaction outputs
   - Validates transactions against current state
   - Enforces no-double-spend rule

4. **Blockchain**
   - Maintains the chain of blocks
   - Handles forks (longest valid chain wins)
   - Validates and adds new blocks

## Implementation Details

### What's Simplified

1. **Cryptography**
   - No real cryptographic signatures
   - Simplified address system (just strings)
   - No peer-to-peer networking

2. **Mining**
   - Simplified difficulty adjustment
   - No mempool (just pending transactions)
   - Fixed block reward

3. **Networking**
   - No network layer
   - Single-node operation only

### Key Invariants

1. **Transaction Validity**
   - All inputs must reference unspent outputs
   - Sum of inputs must be ≥ sum of outputs
   - No double-spending within a block

2. **Block Validity**
   - Valid PoW (hash meets difficulty target)
   - All transactions in the block are valid
   - Correct reference to previous block

3. **UTXO Consistency**
   - UTXO set is updated atomically with block addition
   - Fork handling maintains consistent UTXO state

## Why UTXO Model?

1. **Parallelism**
   - Transactions spending different UTXOs can be processed in parallel
   - No global state to synchronize

2. **Privacy**
   - No account balances to track
   - Each transaction uses fresh addresses

3. **Simplicity**
   - Stateless validation
   - Clear transaction dependencies

## What Breaks Without Double-Spend Protection?

Removing the double-spend check would allow:
1. **Inflation** - Creating money from nothing
2. **Theft** - Spending the same coins multiple times
3. **Network Inconsistency** - Different nodes could have different views of the ledger

## Running the Code

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the CLI:
   ```bash
   python -m src.main
   ```

## CLI Commands

1. **Create Transaction** - Create and validate a new transaction
2. **Mine Block** - Mine a new block with pending transactions
3. **View Blockchain** - Explore blocks and transactions
4. **View UTXO Set** - See all unspent transaction outputs
5. **Simulate Fork** - Create an alternative chain
6. **Check Balance** - View balance for an address

## Architecture

```
src/
├── blockchain/
│   ├── __init__.py
│   ├── block.py       # Block structure and mining
│   ├── transaction.py # Transaction handling
│   ├── utxo.py        # UTXO set management
│   └── blockchain.py  # Core blockchain logic
└── main.py           # CLI interface
```

## Limitations

1. **No Persistence** - All data is in-memory
2. **No Networking** - Single-node only
3. **No Real Cryptography** - Simplified security model
4. **No Smart Contracts** - Simple value transfer only

## Learning Resources

- [Bitcoin Whitepaper](https://bitcoin.org/bitcoin.pdf)
- [Mastering Bitcoin](https://github.com/bitcoinbook/bitcoinbook)
- [Building Blockchain in Go](https://jeiwan.cc/posts/building-blockchain-in-go-part-1/)
