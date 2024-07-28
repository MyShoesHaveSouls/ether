import random
import asyncio
import aiohttp
from Crypto.Hash import keccak
import ecdsa
import binascii
from discordwebhook import Discord
from numba import jit

# Function to get user input with validation
def get_user_input(prompt, condition):
    while True:
        try:
            value = int(input(prompt))
            if not condition(value):
                print(f"Invalid input: {prompt}")
                continue
            return value
        except ValueError:
            print("Error: value should be in integer format")

# Collecting user inputs
start_value = get_user_input("Start value: ", lambda x: x > 0)
end_value = get_user_input("End value: ", lambda x: x > start_value)
number_of_threads = get_user_input("Number of threads: ", lambda x: x > 0)
no_of_accounts = get_user_input("Number of accounts per batch: ", lambda x: x > 0)
check_in_thread = (end_value - start_value) // number_of_threads

# Discord notification function
def discord_notification(msg):
    try:
        webhook_url = "https://discord.com/api/webhooks/1237273754414092328/TKG1nt0b7VCWspq-oFpModKHWLcsQB-aAaNBLHxYDSJXDIa-c9OF0J6WH2n9L-UjwPPh"
        discord = Discord(url=webhook_url)
        discord.post(content=msg)
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

# List of API keys
api_keys = [
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

# Function to generate Ethereum address from private key
@jit(nopython=True)
def generate_address(private_key):
    private_key_hex = hex(private_key)[2:].zfill(64)
    sk = ecdsa.SigningKey.from_string(binascii.unhexlify(private_key_hex), curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    public_key = vk.to_string()
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(public_key)
    public_key_hash = keccak_hash.digest()
    ethereum_address = "0x" + public_key_hash.hex()[-40:]
    return ethereum_address

# Function to get balance of Ethereum addresses
async def get_balance(addresses, api_key):
    address_str = ','.join(addresses)
    url = f'https://api.etherscan.io/api?module=account&action=balancemulti&address={address_str}&tag=latest&apikey={api_key}'
    async with aiohttp.ClientSession() as session:
        for _ in range(5):  #