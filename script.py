import threading
import requests
from eth_account import Account
from queue import Queue
import itertools
from decimal import Decimal, getcontext

# Set precision high enough to avoid scientific notation
getcontext().prec = 18

# Etherscan API keys (replace with your actual API keys)
API_KEYS = [
    '5K221ME7PYP5RUE1E1CBCB8WU2UV3EMKDS',
    'QQVKPQFWG7X2NU67549KEEH2RMVJS3KCPW',
    'JPPXZJ51MRYMKWBXMPCU266M6DNK8J5MXR',
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
def check_balance(address, api_key):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    if data['status'] == '1':
        return Decimal(data['result']) / Decimal(1e18)  # Convert wei to ether using Decimal
    return Decimal(0)

# Minimum balance threshold in ETH for printing
MIN_BALANCE = Decimal('0.1')  # Set to desired value, e.g., 0.1 ETH for a minimum balance of 0.1 ETH

# Worker function for threading
def worker(queue, api_keys_iter):
    while not queue.empty():
        private_key_int = queue.get()
        address, private_key = generate_address(private_key_int)
        api_key = next(api_keys_iter)
        balance = check_balance(address, api_key)
        if balance > MIN_BALANCE:
            formatted_balance = f"{balance:.18f}".rstrip('0').rstrip('.')
            print(f'Match found! Address: {address}, Private Key: {private_key}, Balance: {formatted_balance} ETH')
        queue.task_done()

def main(start, end, num_threads):
    queue = Queue()
    for i in range(start, end):
        queue.put(i)
    
    # Create an infinite iterator for API keys to cycle through them
    api_keys_iter = itertools.cycle(API_KEYS)

    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(queue, api_keys_iter))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    start_value = int(input("Enter the starting value (integer): "))
    end_value = int(input("Enter the ending value (integer): "))
    num_threads = int(input("Enter the number of threads to use: "))
    
    main(start_value, end_value, num_threads)
