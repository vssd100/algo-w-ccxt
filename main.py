from datahandle import DataHandling
from config import API_KEY, API_SECRET, URL_WEBHOOK
import pandas as pd
import ccxt
import time
import sys
import requests
import io

exchange = ccxt.binance({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "enableRateLimit": True
})
exchange.set_sandbox_mode(True) 

def loop(exchange):
    datafetch = DataHandling()
    ohlc = datafetch.DataFetching(limit=1000)
    data = datafetch.DataPreparation(ohlc)
    signals = pd.DataFrame(data)

    balance = exchange.fetch_balance()
    wage = balance['free']['USDT'] * 0.1
    
    latest_signal = signals.iloc[-1]
    previous_signal = signals.iloc[-2]

    balance = exchange.fetch_balance()
    wage = balance['free']['USDT'] * 0.1

    if latest_signal['BuySignal'] != latest_signal['SellSignal']:
        # Buy
        if latest_signal['BuySignal'] == 1 and previous_signal['BuySignal'] != 1:
            amount_to_buy = wage / latest_signal['close']  
            try:
                exchange.create_order("BTC/USDT", "market", "buy", amount_to_buy)
                print("Bought BTC:", amount_to_buy)
            except Exception as e:
                print("Buy failed:", e)
                
        # Sell
        elif latest_signal['SellSignal'] == 1 and previous_signal['SellSignal'] != 1:
            btc_free = balance['free']['BTC']
            if btc_free > 0:
                try:
                    exchange.create_order("BTC/USDT", "market", "sell", btc_free)

                    last_buy_price = signals.loc[signals['BuySignal'] == 1, 'close'].iloc[-1]
                    last_sell_price = latest_signal['close']
                    profit = (last_sell_price - last_buy_price) / last_buy_price

                    
                    
                    print(f"Sold BTC: {btc_free}, Profit: {profit:.2%}.")
                except Exception as e:
                    print("Sell failed:", e)
    else:
        print("No trade executed")

WEBHOOK_URL = URL_WEBHOOK
class DiscordBuffer:
    def __init__(self):
        self.buffer = io.StringIO()

    def write(self, message):
        self.buffer.write(message)

    def flush(self):
        content = self.buffer.getvalue().strip()
        if content:
            try:
                requests.post(WEBHOOK_URL, json={"content": f"```{content}```"}, timeout=3)
            except Exception as e:
                sys.__stdout__.write(f"[Webhook error] {e}\n")
        self.buffer = io.StringIO()  # reset buffer

discord_logger = DiscordBuffer()
sys.stdout = discord_logger
sys.stderr = discord_logger

while True:
    loop(exchange)

    balance = exchange.fetch_balance()
    
    usdt = balance['free']['USDT']  
    btc = balance['free']['BTC']

    ticker = exchange.fetch_ticker("BTC/USDT")
    btc_price = ticker['last']

    portfolio_value = usdt + (btc * btc_price)

    print(f"Portfolio value: {portfolio_value:.2f}")
    print("Going to sleep for 5 minutes.")

    discord_logger.flush()

    time.sleep(300)

