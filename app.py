import bdkpython as bdk
import requests
ESPLORA_URL = "https://blockstream.info/testnet/api"# Testnet Explorer API

def get_transactions(wallet):
    try:
        address_info = wallet.next_unused_address(bdk.KeychainKind.EXTERNAL) 
        
        bitcoin_address = address_info.address  
        print(f"\nFetching transactions for address: {bitcoin_address}")

        url = f"{ESPLORA_URL}/address/{bitcoin_address}/txs"
        print(f"Requesting: {url}")  
        response = requests.get(url)

        if response.status_code == 200:
            txs = response.json()
            if txs:
                print("\nTransaction History (TXIDs):")
                for tx in txs:
                    txid = tx["txid"]
                    confirmations = tx.get("status", {}).get("block_height", "Unconfirmed")
                    print(f"TXID: {txid} | Confirmations: {confirmations}")
            else:
                print("\nOOps !! No transactions found  >  No TXID")
        else:
            print(f" Error fetching transactions: {response.status_code}")

    except Exception as e:
        print(f" Exception in fetching transactions: {e}")

def main():
    # Create a new mnemonic
    print("........Generating mnemonic seed......")
    mnemonic = bdk.Mnemonic(bdk.WordCount.WORDS12)
    print(f"Mnemonic: {mnemonic}")
    
    # Create master key
    network = bdk.Network.TESTNET
    master_key = bdk.DescriptorSecretKey(network, mnemonic, "")
    
    try:
        
        xprv = master_key.as_string().replace("/*", "")
        template = f"wpkh({xprv}/84h/1h/0h/0/*)"
        change_template = f"wpkh({xprv}/84h/1h/0h/1/*)"
        
        print(f"Trying descriptor template: {template}")
        
        # Create descriptors
        descriptor = bdk.Descriptor(template, network)
        change_descriptor = bdk.Descriptor(change_template, network)
        
        # Create an in-memory database connection
        print("\nSetting up in-memory database connection...")
        connection = bdk.Connection.new_in_memory()
        print("Created in-memory connection")
        
        print("\n..........Creating a  wallet..............")
        wallet = bdk.Wallet(
            descriptor=descriptor,
            change_descriptor=change_descriptor,
            network=network,
            connection=connection
        )
        print("\n Successfully created wallet!!")
                
        print("\n..........Wallet Details..............")
        # wallet details
        print(f"Network: {wallet.network()}")
        
        #t wallet object representation
        print(f"\nWallet object: {wallet}")
        
        # wallet descriptor details
        try:
            print(f"\nDescriptor checksum: {wallet.descriptor_checksum()}")
        except:
            print("\nCould not retrieve descriptor checksum")
        
        # derivation index info
        try:
            external_index = wallet.derivation_index(bdk.KeychainKind.EXTERNAL)
            internal_index = wallet.derivation_index(bdk.KeychainKind.INTERNAL)
            print(f"\nCurrent derivation indices:")
            print(f"  External: {external_index}")
            print(f"  Internal: {internal_index}")
        except Exception as e:
            print(f"\nCould not retrieve derivation indices: {e}")
        
        print("\n......Setting up ElectrumClient for blockchain interaction.........")
        electrum_url = "ssl://electrum.blockstream.info:60002"
        electrum_client = bdk.ElectrumClient(electrum_url)
        
        # The version am using  doesn't have wallet.sync(), but has electrum_client.sync()
        print("Connecting to Electrum server...")
        try:
            # Test the connection with a ping
            electrum_client.ping()
            print("Successfully connected to Electrum server")
            
            #Fee estimates
            fee = electrum_client.estimate_fee(6)  #6 block target
            print(f"Estimated fee for 6 blocks: {fee}")
            
        except Exception as e:
            print(f"Error connecting to Electrum server: {e}")
        
        # Get balance
        print("\n----- Wallet Balance -----")
        balance = wallet.balance()
        print(f"Balance object: {balance}")
        
        # Extract balance components if it's an object with properties
        try:
            print(f"Confirmed balance: {balance.confirmed} satoshis")
            print(f"Unconfirmed balance: {balance.unconfirmed} satoshis")
            print(f"Total balance: {balance.total} satoshis")
            total_btc = float(balance.total) / 100_000_000
            print(f"Total BTC: {total_btc:.8f}")
        except:
            # If balance is just a number
            try:
                total_btc = float(balance) / 100_000_000
                print(f"Total balance: {balance} satoshis ({total_btc:.8f} BTC)")
            except:
                print(f"Balance is of type: {type(balance)}")
        
        # Generate addresses
        print("\n------ Wallet Addresses ------------")
        try:
            external_address = wallet.next_unused_address(bdk.KeychainKind.EXTERNAL)
            print(f"Receive address (My ADDRESS): {external_address}")
        except Exception as e:
            print(f"Could not generate receive address with next_unused_address: {e}")
            try:
                external_address = wallet.reveal_next_address(bdk.KeychainKind.EXTERNAL)
                print(f"Receive address (reveal_next_address): {external_address}")
            except Exception as e:
                print(f"Could not generate receive address with reveal_next_address: {e}")
        
        # Get a change address
        try:
            internal_address = wallet.next_unused_address(bdk.KeychainKind.INTERNAL)
            print(f"Change address: {internal_address}")
        except Exception as e:
            print(f"Could not generate change address with next_unused_address: {e}")
            try:
                internal_address = wallet.reveal_next_address(bdk.KeychainKind.INTERNAL)
                print(f"Change address (reveal_next_address): {internal_address}")
            except Exception as e:
                print(f"Could not generate change address with reveal_next_address: {e}")
        
            
        print("\n......Fetching transaction history.......")
        get_transactions(wallet)

    except Exception as e:
        print(f"Error: {e}")
        print("\nDebugging bdkpython module:")
        

if __name__ == "__main__":
    main()