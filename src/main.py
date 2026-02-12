import os
import sys
import json
from typing import List, Optional
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.blockchain.blockchain import Blockchain
from src.blockchain.transaction import Transaction, TransactionInput, TransactionOutput

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"{title:^60}")
    print("=" * 60)

def create_transaction(blockchain: Blockchain) -> None:
    """CLI to create and add a new transaction."""
    print_header("CREATE TRANSACTION")
    
    # Get inputs
    inputs = []
    while True:
        print("\nAdd input (leave txid empty to finish):")
        txid = input("Previous transaction ID: ").strip()
        if not txid:
            if not inputs and not blockchain.utxo.utxos:
                print("No UTXOs available. You need to mine a block first!")
                input("\nPress Enter to continue...")
                return
            break
            
        try:
            output_index = int(input("Output index: ").strip())
            signature = input("Signature (mock): ").strip() or "mock_signature"
            inputs.append(TransactionInput(txid=txid, output_index=output_index, signature=signature))
            print("Input added. Add another or press Enter to continue.")
        except ValueError:
            print("Invalid output index. Please enter a number.")
    
    # Get outputs
    outputs = []
    while True:
        print("\nAdd output (leave recipient empty to finish):")
        recipient = input("Recipient address: ").strip()
        if not recipient:
            break
            
        try:
            value = int(input("Amount: ").strip())
            outputs.append(TransactionOutput(value=value, recipient=recipient))
            print("Output added. Add another or press Enter to continue.")
        except ValueError:
            print("Invalid amount. Please enter a number.")
    
    if not inputs or not outputs:
        print("Transaction must have at least one input and one output.")
        input("\nPress Enter to continue...")
        return
    
    # Create and add transaction
    tx = Transaction(inputs=inputs, outputs=outputs)
    if blockchain.add_transaction(tx):
        print(f"\n✅ Transaction added to pending transactions!")
        print(f"Transaction ID: {tx.txid}")
    else:
        print("\n❌ Invalid transaction! Check that inputs reference unspent outputs.")
    
    input("\nPress Enter to continue...")

def mine_block(blockchain: Blockchain) -> None:
    """CLI to mine a new block."""
    print_header("MINE BLOCK")
    
    if not blockchain.pending_transactions:
        print("No pending transactions to mine!")
        input("\nPress Enter to continue...")
        return
    
    miner_address = input("Enter your miner address: ").strip() or "miner_address"
    
    print("\nMining block...")
    block = blockchain.mine_block(miner_address)
    
    if block:
        print(f"\n✅ Block mined successfully!")
        print(f"Block hash: {block.hash}")
        print(f"Block index: {block.index}")
        print(f"Transactions in block: {len(block.transactions)}")
    else:
        print("\n❌ Failed to mine block!")
    
    input("\nPress Enter to continue...")

def view_blockchain(blockchain: Blockchain) -> None:
    """CLI to view the blockchain."""
    print_header("BLOCKCHAIN EXPLORER")
    
    print(f"Chain length: {len(blockchain.chain)}")
    print(f"Pending transactions: {len(blockchain.pending_transactions)}")
    print(f"Active forks: {len(blockchain.forks)}")
    
    view_option = input("\nView (1) full chain or (2) specific block? ").strip()
    
    if view_option == "2":
        try:
            block_index = int(input("Enter block index: ").strip())
            if 0 <= block_index < len(blockchain.chain):
                print_block(blockchain.chain[block_index])
            else:
                print("Invalid block index!")
        except ValueError:
            print("Please enter a valid number!")
    else:
        for i, block in enumerate(blockchain.chain):
            print(f"\n--- Block {i} ---")
            print(f"Hash: {block.hash}")
            print(f"Previous hash: {block.previous_hash}")
            print(f"Nonce: {block.nonce}")
            print(f"Transactions: {len(block.transactions)}")
            
            if i > 0 and input("\nView transactions? (y/n): ").lower() == 'y':
                for tx in block.transactions:
                    print(f"\n  TX: {tx.txid[:16]}...")
                    print(f"  Inputs: {len(tx.inputs)}")
                    for inp in tx.inputs:
                        print(f"    - {inp.txid[:8]}...:{inp.output_index}")
                    print(f"  Outputs: {len(tx.outputs)}")
                    for out in tx.outputs:
                        print(f"    - {out.recipient[:8]}...: {out.value}")
    
    input("\nPress Enter to continue...")

def view_utxo(blockchain: Blockchain) -> None:
    """CLI to view the UTXO set."""
    print_header("UNSPENT TRANSACTION OUTPUTS (UTXO)")
    
    if not blockchain.utxo.utxos:
        print("No UTXOs available. Mine a block to create some!")
        input("\nPress Enter to continue...")
        return
    
    address = input("Filter by address (leave empty to show all): ").strip()
    
    print("\nUTXOs:")
    total = 0
    for (txid, idx), output in blockchain.utxo.utxos.items():
        if not address or output.recipient == address:
            print(f"- {txid[:8]}...:{idx} -> {output.recipient[:8]}...: {output.value}")
            if output.recipient == address:
                total += output.value
    
    if address:
        print(f"\nTotal for {address[:8]}...: {total}")
    
    input("\nPress Enter to continue...")

def simulate_fork(blockchain: Blockchain) -> None:
    """CLI to simulate a fork in the blockchain."""
    print_header("SIMULATE FORK")
    
    if len(blockchain.chain) < 2:
        print("Need at least 2 blocks to create a fork!")
        input("\nPress Enter to continue...")
        return
    
    # Create a fork by mining a block that extends from an earlier block
    fork_point = min(1, len(blockchain.chain) - 1)  # At least block 1
    
    print(f"Creating fork at block {fork_point}...")
    
    # Create a transaction for the fork
    tx = Transaction(
        inputs=[],  # This would be a valid input in a real implementation
        outputs=[TransactionOutput(value=10, recipient="fork_address")]
    )
    
    # Create and mine the forked block
    forked_block = Block(
        index=fork_point + 1,
        transactions=[tx],
        previous_hash=blockchain.chain[fork_point].hash,
        difficulty=blockchain.difficulty
    )
    forked_block.mine()
    
    # Add to forks
    fork_chain = blockchain.chain[:fork_point + 1] + [forked_block]
    blockchain.forks.append(fork_chain)
    
    print(f"\n✅ Fork created at block {fork_point}!")
    print(f"Main chain length: {len(blockchain.chain)}")
    print(f"Fork chain length: {len(fork_chain)}")
    print("\nThe fork will be automatically adopted if it becomes longer than the main chain.")
    
    input("\nPress Enter to continue...")

def print_menu() -> None:
    """Print the main menu."""
    print_header("UTXO BLOCKCHAIN SIMULATOR")
    print("1. Create Transaction")
    print("2. Mine Block")
    print("3. View Blockchain")
    print("4. View UTXO Set")
    print("5. Simulate Fork")
    print("6. Check Balance")
    print("7. Exit")

def main():
    """Main entry point for the CLI."""
    # Initialize blockchain
    blockchain = Blockchain(difficulty=2)  # Lower difficulty for testing
    
    while True:
        clear_screen()
        print_menu()
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        try:
            if choice == '1':
                create_transaction(blockchain)
            elif choice == '2':
                mine_block(blockchain)
            elif choice == '3':
                view_blockchain(blockchain)
            elif choice == '4':
                view_utxo(blockchain)
            elif choice == '5':
                simulate_fork(blockchain)
            elif choice == '6':
                address = input("Enter address to check balance: ").strip()
                if address:
                    balance = blockchain.get_balance(address)
                    print(f"\nBalance for {address[:8]}...: {balance}")
                    input("\nPress Enter to continue...")
            elif choice == '7':
                print("\nExiting...")
                break
            else:
                print("\nInvalid choice. Please try again.")
                input("Press Enter to continue...")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
