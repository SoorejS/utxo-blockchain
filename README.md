# UTXO Blockchain: A Minimal Implementation

## 1. Project Purpose

This project is a minimal, educational implementation of a UTXO-based blockchain, focusing on correctness and core Bitcoin principles. It serves as a learning tool for understanding the fundamental mechanics of Bitcoin's transaction validation and blockchain state management.

### Key Characteristics:
- **Correctness-First**: Prioritizes accurate implementation of core validation rules over performance optimizations
- **UTXO Model**: Implements Bitcoin's Unspent Transaction Output model for transaction validation
- **Educational Focus**: Designed to be studied and understood, not deployed in production

### Explicit Non-Goals:
- ❌ No networking layer (single-node only)
- ❌ No full scripting system (simplified transaction model)
- ❌ No production-grade security measures
- ❌ No peer-to-peer protocol implementation

## 2. Core Invariants Enforced

### 2.1 No Double Spending
- **Rule**: Each UTXO can only be spent once
- **Violation Impact**: Enables inflation by allowing the same coins to be spent multiple times

### 2.2 UTXO Atomicity
- **Rule**: State transitions are atomic - either all changes in a block are applied or none are
- **Violation Impact**: Could lead to inconsistent state where some UTXOs are spent without corresponding outputs

### 2.3 Input/Output Value Conservation
- **Rule**: For non-coinbase transactions: Sum(inputs) ≥ Sum(outputs)
- **Violation Impact**: Allows creation of coins from nothing, breaking the fixed supply model

### 2.4 Block Validation Precedence
- **Rule**: Blocks must pass PoW validation before any state changes
- **Violation Impact**: Could allow invalid blocks to affect the UTXO set

### 2.5 Block-Level Double-Spend Detection
- **Rule**: No two transactions in the same block can spend the same UTXO
- **Violation Impact**: Could allow double-spending within the same block

## 3. State Transition Model

The core state transition is formally defined as:

```
UTXO(n+1) = Apply(Block_n, UTXO(n))
```

### Implementation Details:
- The UTXO set is maintained in memory and updated atomically
- Each block's transactions are validated in order
- State transitions are all-or-nothing (atomic)

In Bitcoin Core, the UTXO set is stored in chainstate and updated atomically during block validation in validation.cpp. This project models that state transition conceptually.

### Node vs. Miner Roles:
- **Miners**: Propose blocks with valid transactions
- **Nodes**: Independently validate all blocks against consensus rules
- **Enforcement**: Every full node enforces all rules, regardless of miner behavior

## 4. Simplifications Compared to Bitcoin

| Component          | This Implementation | Bitcoin Core |
|-------------------|---------------------|--------------|
| Cryptography      | Mock signatures     | ECDSA + BIP340 |
| Scripting         | None                | Full Script  |
| Merkle Tree       | Simple binary       | Double-SHA256 |
| Difficulty        | Fixed               | Adjusts every 2016 blocks |
| Network           | None                | P2P network  |
| Mempool           | Simple list         | Policy layer |
| Storage           | In-memory           | LevelDB + UTXO cache |

## 5. Fork Handling

### 5.1 Consensus Rule
The valid chain is the one with the most accumulated proof-of-work, not necessarily the longest chain by block count.

### 5.2 Key Concepts:
- **Chain Work**: Chain work is derived from the target threshold encoded in each block header. Bitcoin selects the chain with the greatest cumulative proof-of-work.
- **Reorgs**: The chain can reorganize if a heavier chain is found
- **Finality**: Transactions gain confidence with each confirmation

### 5.3 Why Not Voting?
- Bitcoin uses proof-of-work, not voting, to establish consensus
- Prevents Sybil attacks that could manipulate voting outcomes
- Aligns incentives through economic security

## 6. Example Invalid Cases

### 6.1 Double Spend in Same Block
```python
# Transaction 1: Spend UTXO A
# Transaction 2: Also tries to spend UTXO A
```
**Result**: Second transaction rejected - violates single-spend rule

### 6.2 Spending Nonexistent UTXO
```python
# Tries to spend non-existent txid:output_index
```
**Result**: Transaction rejected - input not in UTXO set

### 6.3 Invalid PoW
```python
# Block with hash that doesn't meet target difficulty
```
**Result**: Block rejected - fails PoW validation

### 6.4 Insufficient Input Value
```python
# Inputs: 5 BTC
# Outputs: 6 BTC
# Fee: -1 BTC (invalid)
```
**Result**: Transaction rejected - violates conservation of value

## 7. Key Learnings

### 7.1 UTXO Advantages
- **Parallel Validation**: UTXOs can be validated independently
- **State Simplification**: No need to track account balances
- **Determinism**: Clear rules for transaction acceptance
- **Stateless Validation**: UTXO model enables stateless validation but does not inherently provide privacy; privacy depends on usage patterns.

### 7.2 Miners vs. Consensus Rules
- Miners propose blocks but don't define rules
- Full nodes independently validate against consensus rules
- This separation prevents miner centralization of rule-making

### 7.3 Proof of Work as Rate Limiter
- PoW serves as a Sybil resistance mechanism
- Difficulty adjustment maintains consistent block time
- Not a source of randomness but a deterministic puzzle

### 7.4 Deterministic Validation
- All nodes must reach the same conclusion about validity
- No room for interpretation in consensus-critical code
- Enables trustless verification of the entire chain

## 8. Why This Matters

This project helped me understand that Bitcoin is not a database but a deterministic state machine enforced independently by full nodes. The separation of concerns between miners (block production) and nodes (validation) is fundamental to Bitcoin's security model. The UTXO model's elegance lies in its simplicity and verifiability, providing strong guarantees about the state of the system without requiring trust in any single participant.

## Getting Started

### Prerequisites
- Python 3.8+
- `cryptography` package

### Installation
```bash
pip install -r requirements.txt
python -m src.main
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.
