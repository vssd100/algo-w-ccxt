import ccxt
import pandas as pd
from smartmoneyconcepts import smc
from config import API_KEY, API_SECRET

class DataHandling:
    def __init__(self):
        self.exchange = ccxt.binance({
            "apiKey": "API_KEY",
            "secret": "API_SECRET",
            "enableRateLimit": True
        })
        self.exchange.set_sandbox_mode(True)  
        self.symbol = "BTC/USDT"
        self. timeframe = "5m"

    def DataFetching(self, limit=1000):
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=limit)
        ohlc = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        ohlc['timestamp'] = pd.to_datetime(ohlc['timestamp'], unit='ms')
        return ohlc

    def DataPreparation(self, ohlc):


        def CalculatePoints(row):

            return points

        df['Points'] = df.apply(CalculatePoints, axis=1)

        df['BuySignal'] = (df['Points'] < -1).map({True: 1, False: 0})
        df['SellSignal'] = (df['Points'] > 1).map({True: 1, False: 0})
        
        signals = df[['timestamp', 'BuySignal', 'SellSignal', 'close']]
        return signals


