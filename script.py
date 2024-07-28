 import asyncio
import aiohttp
from discordwebhook import Discord

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

print(f"Start value: {start_value}")
print(f"End value: {end_value}")
print(f"Number of threads: {number_of_threads}")
print(f"Number of accounts per batch: {no_of_accounts}")
print(f"Check in thread: {check_in_thread}")

# Discord notification function
def discord_notification(msg):
    try:
        webhook_url = "https://discord.com/api/webhooks/1237273754414092328/TKG1nt0b7VCWspq-oFpModKHWLcsQB-aAaNBLHxYDSJXDIa-c9OF0J6WH2n9L-UjwPPh"
        discord = Discord(url=webhook_url)
        discord.post(content=msg)
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

# Placeholder functions for generate_address and get_balance
async def generate_address(private_key):
    return f"0x{private_key:064x}"

async def get_balance(addresses, api_key):
    return {"status": "1", "result": [{"account": addr, "balance": "0"} for addr in addresses]}

# Function to process the balance response
async def process_balance_response(response, count, no_of_accounts):
    if response['status'] != '1':
        return False
    for index, rec in enumerate(response['result']):
        hex_id = count - no_of_accounts + index
        balance = int(rec['balance'])
        address = rec['account']
        if balance > 3000000000000000:
            print(f"Found good balance, private-key {hex(hex_id)[2:].zfill(64)}")
            discord_notification(f"Private Key: {hex(hex_id)[2:].zfill(64)}: balance: {balance / 1e18}")
        elif balance > 0:
            print(f"{hex_id} {address} {balance / 1e18}")
    return True

# Function to run the balance check process
async def run(start, thread_index):
    count = start
    while count < start + check_in_thread:
        addresses = [await generate_address(count + i) for i in range(no_of_accounts)]
        api_key = 'FAKE_API_KEY'  # Use a single API key for simplicity
        response = await get_balance(addresses, api_key)
        if response and await process_balance_response(response, count, no_of_accounts):
            count += no_of_accounts
        else:
            await asyncio.sleep(5)

# Function to run multiple threads
async def run_multiple_threads():
    tasks = []
    global start_value
    for thread_index in range(number_of_threads):
        tasks.append(run(start_value, thread_index))
        start_value += check_in_thread
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(run_multiple_threads())
    except Exception as e:
        discord_notification(f"Server 01: Failed to run, restart it. {e}")
   
