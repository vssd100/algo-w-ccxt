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
        fvg = smc.fvg(ohlc, join_consecutive=False)
        swing_highs_lows = smc.swing_highs_lows(ohlc, swing_length=50)
        bos_choch = smc.bos_choch(ohlc, swing_highs_lows, close_break=True)
        order_blocks = smc.ob(ohlc, swing_highs_lows, close_mitigation=False)
        liquidity = smc.liquidity(ohlc, swing_highs_lows, range_percent=0.01)
        previous_highs_lows = smc.previous_high_low(ohlc, time_frame="15m")
        retracements = smc.retracements(ohlc, swing_highs_lows)
        merged_df = pd.concat([fvg, swing_highs_lows, bos_choch, order_blocks, liquidity, previous_highs_lows, retracements], axis=1)

        merged_df.fillna(0, inplace=True)

        merged_df.reset_index(inplace=True)
        ohlc.reset_index(inplace=True)
        df = pd.concat([ohlc, merged_df], axis=1)

        def CalculatePoints(row):
            points = 0
            points += 1 if row['FVG'] == 1 else -1 if row['FVG'] == -1 else 0
            points += 1 if row['BOS'] == 1 else -1 if row['BOS'] == -1 else 0
            points += -1 if row['CHOCH'] == 1 else -1 if row['CHOCH'] == -1 else 0
            points += 1 if row['OB'] == 1 else -1 if row['OB'] == -1 else 0
            points += 1 if row['Liquidity'] == 1 else -1 if row['Liquidity'] == -1 else 0
            points += 1 if row['Direction'] == 1 else -1 if row['Direction'] == -1 else 0
            return points

        df['Points'] = df.apply(CalculatePoints, axis=1)

        df['BuySignal'] = (df['Points'] < -1).map({True: 1, False: 0})
        df['SellSignal'] = (df['Points'] > 1).map({True: 1, False: 0})
        
        signals = df[['timestamp', 'BuySignal', 'SellSignal', 'close']]
        return signals


