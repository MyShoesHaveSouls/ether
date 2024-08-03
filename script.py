import threading
import requests
from eth_account import Account
from queue import Queue

# Etherscan API key (replace with your actual API key)
API_KEY = 'YourEtherscanAPIKey'

# Function to generate Ethereum address from a private key
def generate_address(private_key_int):
    private_key = hex(private_key_int)[2:].zfill(64)
    account = Account.from_key(private_key)
    return account.address, private_key

# Function to check the balance of an Ethereum address using Etherscan API
def check_balance(address):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data['status'] == '1':
        return int(data['result']) / 1e18  # Convert wei to ether
    return 0

# Worker function for threading
def worker(queue):
    while not queue.empty():
        private_key_int = queue.get()
        address, private_key = generate_address(private_key_int)
        balance = check_balance(address)
        if balance > 0:
            print(f'Match found! Address: {address}, Private Key: {private_key}, Balance: {balance} ETH')
        queue.task_done()

def main(start, end, num_threads):
    queue = Queue()
    for i in range(start, end):
        queue.put(i)
    
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(queue,))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    start_value = int(input("Enter the starting value (integer): "))
    end_value = int(input("Enter the ending value (integer): "))
    num_threads = int(input("Enter the number of threads to use: "))
    
    main(start_value, end_value, num_threads)
