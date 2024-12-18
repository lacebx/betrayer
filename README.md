# DexBot

DexBot is a Telegram bot that monitors tokens on Dexscreener and performs actions based on specific conditions, such as checking for rug pulls and fake trading volumes. It sends notifications to a specified Telegram chat when it identifies blacklisted tokens or eligible tokens for trading.

## Features

- Monitors tokens on Dexscreener.
- Checks for rug pulls using the RugCheck API.
- Detects fake trading volumes based on a configurable threshold.
- Sends notifications to a Telegram chat.
- Executes trades via BonkBot API.

## Requirements

- Python 3.x
- `requests` library
- `python-telegram-bot` library

## Installation

1. Clone the repository or download the files.
2. Navigate to the project directory.
3. Install the required packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `config.json` file in the project directory with the following structure:

   ```json
   {
       "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
       "telegram_chat_id": "YOUR_TELEGRAM_CHAT_ID",
       "dexscreener_api_url": "https://api.dexscreener.com/tokens",
       "bonkbot_api_url": "https://api.bonkbot.com/trade",
       "volume_threshold": 1000,
       "trade_amount": 0.1,
       "poll_interval": 60
   }
   ```

   Replace the placeholder values with your actual configuration.

## Usage

To run the bot, execute the following command in your terminal:

```bash
python dexbot.py
```


The bot will start monitoring tokens and will send notifications to your specified Telegram chat based on the conditions defined in the code.

## Contributing

If you would like to contribute to this project, feel free to submit a pull request or open an issue for discussion.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [RugCheck API](https://rugcheck.xyz/)
- [Dexscreener](https://dexscreener.com/)
