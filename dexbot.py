import json
import requests
import time
from telegram import Bot

# Load configuration from config file
with open("config.json") as config_file:
    config = json.load(config_file)

# Telegram Bot Setup
bot = Bot(token=config["telegram_bot_token"])

# Global Blacklist (Coin & Dev)
coin_blacklist = set()
dev_blacklist = set()

# Helper: Send Telegram Notifications
def send_telegram_message(message):
    bot.send_message(chat_id=config["telegram_chat_id"], text=message)

# Helper: RugCheck API Validation
def check_rug_status(contract_address):
    response = requests.get(f"https://api.rugcheck.xyz/check/{contract_address}")
    if response.status_code == 200:
        data = response.json()
        return data["status"] == "Good"
    return False

# Helper: Check for Fake Volume
def is_fake_volume(token_data):
    try:
        volume = token_data.get("volume", 0)
        buy_volume = token_data.get("buyVolume", 0)
        sell_volume = token_data.get("sellVolume", 0)
        
        # Check if volume ratios are abnormal
        if buy_volume + sell_volume == 0:
            return True
        buy_sell_ratio = buy_volume / (buy_volume + sell_volume)
        return volume < config["volume_threshold"] or not (0.3 < buy_sell_ratio < 0.7)
    except Exception as e:
        print(f"Error checking fake volume: {e}")
        return True

# Helper: Check Liquidity
def has_sufficient_liquidity(token_data):
    try:
        liquidity = token_data.get("liquidity", {}).get("total", 0)
        return liquidity >= config["min_liquidity"]
    except Exception as e:
        print(f"Error checking liquidity: {e}")
        return False

# Main: Monitor Dexscreener
def monitor_dexscreener():
    while True:
        try:
            response = requests.get(config["dexscreener_api_url"])
            if response.status_code == 200:
                tokens = response.json().get("tokens", [])

                for token in tokens:
                    contract = token["contract"]
                    dev_address = token.get("developer")

                    # Skip blacklisted coins/devs
                    if contract in coin_blacklist or dev_address in dev_blacklist:
                        continue

                    # Validate token using RugCheck, volume, and liquidity checks
                    if not check_rug_status(contract):
                        coin_blacklist.add(contract)
                        dev_blacklist.add(dev_address)
                        send_telegram_message(f"Blacklisted rug token: {contract}")
                        continue

                    if is_fake_volume(token):
                        coin_blacklist.add(contract)
                        send_telegram_message(f"Blacklisted fake volume token: {contract}")
                        continue

                    if not has_sufficient_liquidity(token):
                        send_telegram_message(f"Skipped due to insufficient liquidity: {contract}")
                        continue

                    # Process eligible tokens
                    send_telegram_message(f"Eligible token found: {token['name']} ({contract})")

                    # Execute trade via BonkBot
                    execute_trade(token)
            else:
                print(f"Error fetching data from Dexscreener: {response.status_code}")
        except Exception as e:
            print(f"Error in monitor loop: {e}")
        time.sleep(config["poll_interval"])

# Execute Trade via BonkBot
def execute_trade(token):
    try:
        trade_data = {
            "action": "buy",
            "token": token["contract"],
            "amount": config["trade_amount"]
        }
        response = requests.post(config["bonkbot_api_url"], json=trade_data)
        if response.status_code == 200:
            send_telegram_message(f"Trade executed: {trade_data}")

            # Add logic for profit-taking and stop-loss
            monitor_trade_profit(token)
        else:
            send_telegram_message(f"Trade failed: {trade_data}")
    except Exception as e:
        print(f"Error executing trade: {e}")

# Monitor Trade Profit and Stop-Loss
def monitor_trade_profit(token):
    try:
        initial_price = token.get("price", 0)
        profit_target = initial_price * (1 + config["profit_threshold"] / 100)
        stop_loss = initial_price * (1 - config["stop_loss_threshold"] / 100)

        while True:
            response = requests.get(f"{config['dexscreener_api_url']}/{token['contract']}")
            if response.status_code == 200:
                current_price = response.json().get("price", 0)

                if current_price >= profit_target:
                    sell_token(token, "profit")
                    break
                elif current_price <= stop_loss:
                    sell_token(token, "stop-loss")
                    break
            time.sleep(config["poll_interval"])
    except Exception as e:
        print(f"Error monitoring trade profit: {e}")

# Sell Token
def sell_token(token, reason):
    try:
        trade_data = {
            "action": "sell",
            "token": token["contract"],
            "amount": config["trade_amount"]
        }
        response = requests.post(config["bonkbot_api_url"], json=trade_data)
        if response.status_code == 200:
            send_telegram_message(f"Sell executed ({reason}): {trade_data}")
        else:
            send_telegram_message(f"Sell failed ({reason}): {trade_data}")
    except Exception as e:
        print(f"Error executing sell: {e}")

if __name__ == "__main__":
    monitor_dexscreener()
