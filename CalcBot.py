import discord
import requests

client = discord.Client()

# Replace with your bot token
TOKEN = 'YOUR_DISCORD_BOT_TOKEN'

# Replace with your OpenSea API key
OPENSEA_API_KEY = 'YOUR_OPENSEA_API_KEY'

# Replace with your Blur.io API key
BLUR_IO_API_KEY = 'YOUR_BLUR_IO_API_KEY'

# List of secondary exchanges to track
SECONDARY_EXCHANGES = [
    {'name': 'Blur', 'url': 'https://api.blurtoshi.com/v1', 'api_key': BLUR_IO_API_KEY},
    {'name': 'OpenSea', 'url': 'https://api.opensea.io/api/v1', 'api_key': OPENSEA_API_KEY}
]

# Command to track trades for a given wallet address
@client.event
async def on_message(message):
    if message.content.startswith('!track'):
        wallet_address = message.content.split()[1]
        trade_history = get_trade_history(wallet_address)
        if trade_history:
            response = 'Here is your trade history:\n'
            for trade in trade_history:
                response += f'{trade["exchange"]}: Trade #{trade["id"]}: {trade["profit_loss"]}\n'
            await message.channel.send(response)
        else:
            await message.channel.send('Sorry, I could not retrieve your trade history.')

# Helper function to retrieve trade history for a given wallet address from all secondary exchanges
def get_trade_history(wallet_address):
    trade_history = []
    for exchange in SECONDARY_EXCHANGES:
        url = f'{exchange["url"]}/events?account_address={wallet_address}&offset=0&limit=50'
        headers = {'Accept': 'application/json', 'X-API-KEY': exchange['api_key']}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            for event in response.json()['events']:
                trade = {}
                trade['exchange'] = exchange['name']
                trade['id'] = event['id']
                trade['profit_loss'] = calculate_profit_loss(event, wallet_address, exchange['name'])
                trade_history.append(trade)
    if trade_history:
        return trade_history
    else:
        return None

# Helper function to calculate profit/loss for a given trade
def calculate_profit_loss(event, wallet_address, exchange_name):
    if exchange_name == 'OpenSea':
        if event['winner_account']['address'] == wallet_address:
            # User was the buyer
            return event['payment_token']['usd_price'] - event['total_price']['usd']
        else:
            # User was the seller
            return event['total_price']['usd'] - event['payment_token']['usd_price']
    elif exchange_name == 'Blur':
        if event['seller'] == wallet_address:
            # User was the seller
            return event['payment']['usd'] - event['price']['usd']
        else:
            # User was the buyer
            return event['price']['usd'] - event['payment']['usd']

# Run the bot
client.run(TOKEN)