from blockchain import Blockchain, Transaction, TransactionInput, TransactionOutput
from typing import List, Dict, Optional
import json

def print_help():
    print("\n=== UTXO Blockchain CLI ===")
    print("1. Create transaction")
    print("2. Mine pending transactions")
    print("3. Check balance")
    print("4. View blockchain")
    print("5. Validate chain")
    print("6. Exit")

def create_transaction(blockchain: Blockchain):
    print("\n=== Create New Transaction ===")
    
    # Get inputs
    inputs = []
    while True:
        print("\nAdd input (leave txid empty to finish):")
        txid = input("Previous transaction ID: ").strip()
        if not txid:
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
        return
    
    # Create and add transaction
    tx = Transaction(inputs=inputs, outputs=outputs)
    if blockchain.add_transaction(tx):
        print(f"\n✅ Transaction added to pending transactions!")
        print(f"Transaction ID: {tx.txid}")
    else:
        print("\n❌ Invalid transaction! Check that inputs reference unspent outputs.")

def mine_block(blockchain: Blockchain):
    print("\n=== Mining Block ===")
    miner_address = input("Enter your miner address: ").strip()
    if not miner_address:
        miner_address = "miner_address"
    
    block = blockchain.mine_pending_transactions(miner_address)
    if block:
        print(f"\n✅ Block mined successfully!")
        print(f"Block hash: {block.hash}")
        print(f"Block index: {block.index}")
        print(f"Transactions in block: {len(block.transactions)}")
    else:
        print("\n❌ No pending transactions to mine!")

def check_balance(blockchain: Blockchain):
    print("\n=== Check Balance ===")
    address = input("Enter address to check: ").strip()
    if not address:
        print("Address cannot be empty!")
        return
    
    balance = blockchain.get_balance(address)
    print(f"\nBalance for {address}: {balance}")

def view_blockchain(blockchain: Blockchain):
    print("\n=== Blockchain ===")
    print(f"Chain length: {len(blockchain.chain)}")
    print(f"Pending transactions: {len(blockchain.pending_transactions)}")
    
    for i, block in enumerate(blockchain.chain):
        print(f"\n--- Block {i} ---")
        print(f"Hash: {block.hash}")
        print(f"Previous hash: {block.previous_hash}")
        print(f"Nonce: {block.nonce}")
        print(f"Transactions: {len(block.transactions)}")
        
        for tx in block.transactions:
            print(f"  TX: {tx.txid[:16]}...")
            print(f"  Inputs: {len(tx.inputs)}")
            for inp in tx.inputs:
                print(f"    - {inp.txid[:8]}...:{inp.output_index}")
            print(f"  Outputs: {len(tx.outputs)}")
            for out in tx.outputs:
                print(f"    - {out.recipient[:8]}...: {out.value}")

def main():
    print("Initializing UTXO Blockchain...")
    blockchain = Blockchain(difficulty=2)
    
    while True:
        print_help()
        choice = input("\nEnter your choice (1-6): ").strip()
        
        try:
            if choice == '1':
                create_transaction(blockchain)
            elif choice == '2':
                mine_block(blockchain)
            elif choice == '3':
                check_balance(blockchain)
            elif choice == '4':
                view_blockchain(blockchain)
            elif choice == '5':
                is_valid = blockchain.is_chain_valid()
                print(f"\nBlockchain is {"valid" if is_valid else "INVALID"}!")
            elif choice == '6':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
