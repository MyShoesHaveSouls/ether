import threading
import requests
from eth_account import Account
from queue import Queue

# Etherscan API key (replace with your actual API key)
API_KEYS  = [
    'F92Z14GE2DTF6PBBYY1YPHPJ438PT3P2VI',
    '4Q5U7HNF4CGTVTGEMGRV5ZU9WYNJ6N7YA5',
    'EX8K12JY7BCVG8RAUU8X2Z6QT2GCF5EYB4',
    'DZHWCIEA2WW86CZEC88IGWG1JFB6JN3VHS',
    'YIDAXPUWHJB21RJVMS1JMXHABMEF67RQWG',
    '12RU83G1ATVA9V4EMM3U45X8BG4RG9PM6T',
    'PYM9U2QD949KZZX23QJ4YZRX3KC3PHAI88',
    'SH884AZJMKIFDMAPSMHTHJUQ3QIRPH827I',
    'PYM9U2QD949KZZX23QJ4YZRX3KC3PHAI88',
    'TDMPDZU8RD4V9FVB66P5S47QETEJ6R61UY'
]

# Function to generate Ethereum address from a private key
def generate_address(private_key_int):
    private_key = hex(private_key_int)[2:].zfill(64)
    account = Account.from_key(private_key)
    return account.address, private_key

# Function to check the balance of an Ethereum address using Etherscan API
def check_balance(address):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={API_KEYS}"
    response = requests.get(url)
    data = response.json()
    if data['status'] == '1':
        return int(data['result']) / 1e18  # Convert wei to ether
    return 0

# Worker function for threading
# Minimum balance threshold in ETH for printing
MIN_BALANCE = 0.0  # Set to desired value, e.g., 0.1 ETH for a minimum balance of 0.1 ETH

# Worker function for threading
def worker(queue):
    while not queue.empty():
        private_key_int = queue.get()
        address, private_key = generate_address(private_key_int)
        balance = check_balance(address)
        if balance > MIN_BALANCE:
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
