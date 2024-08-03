import threading
import requests
from eth_account import Account
from queue import Queue
import itertools
import time
from decimal import Decimal, getcontext

# Set precision high enough to avoid scientific notati
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

# Maximum rate of API calls per second per API key
REQUESTS_PER_SECOND = 20
INTERVAL = 1.0 / REQUESTS_PER_SECOND

# Batch size for processing addresses
BATCH_SIZE = 5  # Adjust as needed based on API rate limits

# Minimum balance threshold in ETH for printing
MIN_BALANCE = Decimal('0.0001')

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

# Function to handle a batch of addresses
def process_batch(addresses, api_key):
    balances = {}
    for address in addresses:
        balance = check_balance(address, api_key)
        if balance > Decimal(0):  # Filter out zero balances
            balances[address] = balance
        time.sleep(INTERVAL)  # Rate limit the requests
    return balances

# Worker function for processing a batch of addresses
def worker(batch_queue, api_keys_iter):
    while not batch_queue.empty():
        batch = batch_queue.get()
        api_key = next(api_keys_iter)
        addresses = [generate_address(pk)[0] for pk in batch]
        balances = process_batch(addresses, api_key)
        for address, balance in balances.items():
            if balance >= MIN_BALANCE:
                formatted_balance = f"{balance:.8f}".rstrip('0').rstrip('.')
                print(f'Match found! Address: {address}, Balance: {formatted_balance} ETH')
        batch_queue.task_done()
        time.sleep(INTERVAL)  # Rate limit the requests

def main(start, end, num_threads):
    # Prepare addresses to process
    queue = Queue()
    batches = [list(range(start + i * BATCH_SIZE, min(end, start + (i + 1) * BATCH_SIZE))) for i in range((end - start) // BATCH_SIZE + 1)]
    for batch in batches:
        queue.put(batch)
    
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
