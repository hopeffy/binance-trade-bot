from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
import os
from binance.client import Client
import talib

# reading env file
load_dotenv(dotenv_path="req.env")

# Reading APIs from environment variables to keep them secure
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# Indicator values per coin
indicators = pd.DataFrame(columns=["Symbol", "RSI_overbought", "RSI_oversold", "RSI_interval", "SMA_short", "SMA_long", "EMA_short", "EMA_long", "MACD_fast", "MACD_slow", "MACD_signal", "interval", "start_time", "end_time"])
indicators.loc[0] = ["BTCUSDT", 70, 30, 14, 10, 30, 9, 21, 12, 26, 9, "1d", "2022-01-01", f'{datetime.now()}']
indicators.loc[1] = ["ETHUSDT", 70, 30, 14, 10, 30, 9, 21, 12, 26, 9, "1d", "2022-01-01", f'{datetime.now()}']
indicators.loc[2] = ["BNBUSDT", 70, 30, 14, 10, 30, 9, 21, 12, 26, 9, "1d", "2022-01-01", f'{datetime.now()}']
indicators.loc[3] = ["ADAUSDT", 70, 30, 14, 10, 30, 9, 21, 12, 26, 9, "1d", "2022-01-01", f'{datetime.now()}']
indicators.loc[4] = ["XRPUSDT", 70, 30, 14, 10, 30, 9, 21, 12, 26, 9, "1d", "2022-01-01", f'{datetime.now()}']
indicators.loc[5] = ["DOGEUSDT", 70, 30, 14, 10, 30, 9, 21, 12, 26, 9, "1d", "2022-01-01", f'{datetime.now()}']

# Trading states
positions = pd.DataFrame(columns=["Symbol", "Entry Price", "Position", "Position Size"])
positions.loc[0] = ["BTCUSDT", 0, False, 0]
positions.loc[1] = ["ETHUSDT", 0, False, 0]
positions.loc[2] = ["BNBUSDT", 0, False, 0]
positions.loc[3] = ["ADAUSDT", 0, False, 0]
positions.loc[4] = ["XRPUSDT", 0, False, 0]
positions.loc[5] = ["DOGEUSDT", 0, False, 0]




# Stock Market and indicator DataFrames for each coin
BTC_df = pd.DataFrame()
ETH_df = pd.DataFrame()
BNB_df = pd.DataFrame()
ADA_df = pd.DataFrame()
XRP_df = pd.DataFrame()
DOGE_df = pd.DataFrame()

client = Client(api_key=api_key, api_secret=api_secret)

# test variables
now = datetime.now()
ETH_symbol = "ETHUSDT"
interval = Client.KLINE_INTERVAL_1DAY
start_time = "2022-01-01"
end_time = "2022-12-31"




def fetch_historical_data(symbol, interval, start_time, end_time):
    """Binance'ten geçmiş veri çeker."""
    bars = client.get_historical_klines(
        symbol=symbol,
        interval=interval,
        start_str=start_time,
        end_str=end_time
    )
    return bars


def bars_to_data_frame(bars):
    """Çekilen bar verisini DataFrame formatına dönüştürür."""
    columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
    df = pd.DataFrame(bars, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ])
    df["Date"] = pd.to_datetime(df["Open Time"], unit="ms")
    df = df[columns].set_index("Date")
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


def calculate_rsi(df, timeperiod):
    """RSI hesaplama."""
    df['RSI_'f'{timeperiod}'] = talib.RSI(df['Close'], timeperiod=timeperiod)
    return df['RSI_'f'{timeperiod}']


def rsi_signal(df, rsi_period, overbought=70, oversold=30):
    """
    RSI sinyali hesaplama.
    - Overbought: Aşırı alım seviyesi (varsayılan 70).
    - Oversold: Aşırı satım seviyesi (varsayılan 30).
    """
    # calculate rsi values
    rsi_column = calculate_rsi(df=df, timeperiod=rsi_period)

    # create rsi signals
    signal_column_name = f'RSI_Signal_{rsi_period}'
    df[signal_column_name] = 0  # default signal value
    df.loc[rsi_column > overbought, signal_column_name] = -1  # sell signal value
    df.loc[rsi_column < oversold, signal_column_name] = 1  # buy signal value
    return df


def calculate_sma(df, timeperiod):
    """SMA hesaplama."""
    close_prices = df['Close']
    df['SMA_'f'{timeperiod}'] = talib.SMA(close_prices, timeperiod=timeperiod)
    return df['SMA_'f'{timeperiod}']


def sma_signal(df, timeperiod):
    """
    SMA sinyal hesaplama.
    - Fiyat SMA'nın üzerindeyse alış sinyali.
    - Fiyat SMA'nın altındaysa satış sinyali.
    """
    sma_column = calculate_sma(df, timeperiod=timeperiod)
    signal_column_name = f'SMA_Signal_{timeperiod}'
    df[signal_column_name] = 0  # Varsayılan sinyal değeri
    df.loc[df['Close'] > sma_column, signal_column_name] = 1  # Alış sinyali
    df.loc[df['Close'] < sma_column, signal_column_name] = -1  # Satış sinyali
    return df


def calculate_ema(df, timeperiod):
    """EMA hesaplama."""
    df['EMA_'f'{timeperiod}'] = talib.EMA(df['Close'], timeperiod=timeperiod)
    return df['EMA_'f'{timeperiod}']


def ema_signal(df, timeperiod):
    """
    EMA sinyal hesaplama.
    - Fiyat EMA'nın üzerindeyse alış sinyali.
    - Fiyat EMA'nın altındaysa satış sinyali.
    """
    ema_column = calculate_ema(df, timeperiod=timeperiod)
    signal_column_name = f'EMA_Signal_{timeperiod}'
    df[signal_column_name] = 0  # Varsayılan sinyal değeri
    df.loc[df['Close'] > ema_column, signal_column_name] = 1  # Alış sinyali
    df.loc[df['Close'] < ema_column, signal_column_name] = -1  # Satış sinyali
    return df


def calculate_macd(df, fastperiod, slowperiod, signalperiod):
    """MACD hesaplama."""
    macd, macd_signal, macd_hist = talib.MACD(df['Close'], fastperiod=fastperiod, slowperiod=slowperiod,
                                              signalperiod=signalperiod)
    df['MACD'] = macd
    df['MACD_Signal'] = macd_signal
    df['MACD_Hist'] = macd_hist
    return df['MACD'], df['MACD_Signal'], df['MACD_Hist']


def macd_signal(df, fastperiod=12, slowperiod=26, signalperiod=9):
    """
    MACD sinyal hesaplama.
    - MACD > MACD Signal: Alış sinyali.
    - MACD < MACD Signal: Satış sinyali.
    """
    macd, macd_signal, macd_hist = calculate_macd(df, fastperiod, slowperiod, signalperiod)
    signal_column_name = 'MACD_Signal'
    df[signal_column_name] = 0  # Varsayılan sinyal değeri
    df.loc[macd > macd_signal, signal_column_name] = 1  # Alış sinyali
    df.loc[macd < macd_signal, signal_column_name] = -1  # Satış sinyali
    return df


def calculate_indicators(df, rsi_period, sma_period, ema_period, macd_fast, macd_slow, macd_signal):
    """Tüm indikatörleri hesaplar."""
    # Parametrelerle fonksiyonları çağır
    df = calculate_rsi(df, timeperiod=rsi_period)
    df = calculate_sma(df, timeperiod=sma_period)
    df = calculate_ema(df, timeperiod=ema_period)
    df = calculate_macd(df, fastperiod=macd_fast, slowperiod=macd_slow, signalperiod=macd_signal)
    return df

def df_per_coin(indicators): 
    global BTC_df, ETH_df, BNB_df, ADA_df, XRP_df, DOGE_df
    for i in range(len(indicators)):
        bars = fetch_historical_data(indicators["Symbol"][i], indicators["interval"][i], indicators["start_time"][i], indicators["end_time"][i])
        df = bars_to_data_frame(bars)
        df = rsi_signal(df, rsi_period=indicators["RSI_interval"][i], overbought=indicators["RSI_overbought"][i], oversold=indicators["RSI_oversold"][i])
        df = sma_signal(df, timeperiod=indicators["SMA_short"][i])
        df = sma_signal(df, timeperiod=indicators["SMA_long"][i])
        df = ema_signal(df, timeperiod=indicators["EMA_short"][i])
        df = ema_signal(df, timeperiod=indicators["EMA_long"][i])
        df = macd_signal(df, fastperiod=indicators["MACD_fast"][i], slowperiod=indicators["MACD_slow"][i], signalperiod=indicators["MACD_signal"][i])

        
        if indicators["Symbol"][i] == "BTCUSDT":
            BTC_df = df
        elif indicators["Symbol"][i] == "ETHUSDT":
            ETH_df = df
        elif indicators["Symbol"][i] == "BNBUSDT":
            BNB_df = df
        elif indicators["Symbol"][i] == "ADAUSDT":
            ADA_df = df
        elif indicators["Symbol"][i] == "XRPUSDT":
            XRP_df = df
        elif indicators["Symbol"][i] == "DOGEUSDT":
            DOGE_df = df
    
# Calculating tp and sl prices
def take_profit(symbol, positions=pd.DataFrame):
    df= f'{symbol}_df'
    entry_price = positions.loc[positions["Symbol"] == symbol, "Entry Price"]
    tp_price = entry_price * 1.02
    return tp_price


def stop_loss(symbol, position):
    df= f'{symbol}_df'
    entry_price = positions.loc[positions["Symbol"] == symbol, "Entry Price"]
    sl_price = entry_price * 0.98
    return sl_price

# Trading actions. Returns true if there is need to SELL
def tp_sl_actions(symbol, positions):
    tp_price = take_profit(symbol, positions)
    sl_price = stop_loss(symbol, positions)
    df= f'{symbol}_df'
    if df.loci[-1]["Close"] >= tp_price:
        return True
        
    elif df["Close"] <= sl_price:
        return True

    return False

def take_decision(symbol, positions):
    df = f'{symbol}_df'
    rsi_signal_value = df.iloc[-1][f"RSI_Signal_{indicators.loc[indicators['Symbol'] == symbol, 'RSI_interval'].values[0]}"]
    sma_signal_short_value = df.iloc[-1][f"SMA_Signal_{indicators.loc[indicators['Symbol'] == symbol, 'SMA_short'].values[0]}"]
    sma_signal_long_value = df.iloc[-1][f"SMA_Signal_{indicators.loc[indicators['Symbol'] == symbol, 'SMA_long'].values[0]}"]
    ema_signal_short_value = df.iloc[-1][f"EMA_Signal_{indicators.loc[indicators['Symbol'] == symbol, 'EMA_short'].values[0]}"]
    ema_signal_long_value = df.iloc[-1][f"EMA_Signal_{indicators.loc[indicators['Symbol'] == symbol, 'EMA_long'].values[0]}"]
    macd_signal_value = df.iloc[-1]["MACD_Signal"]
    
    






def main():
    # Geçmiş verileri çek
    print("Geçmiş veriler çekiliyor...")
    print(indicators["Symbol"][0], indicators["interval"][0], indicators["start_time"][0], indicators["end_time"][0])
    df_per_coin(indicators)
    print(BTC_df.tail(30))
    print(ETH_df.tail(30))
    print(BNB_df.tail(30))
    print(ADA_df.tail(30))
    print(XRP_df.tail(30))
    print(DOGE_df.tail(30))

    

    


# Bu bölümde çalıştırılmasını istediğiniz kodları ekleyebilirsiniz
if __name__ == "__main__":
    # Burada çalışmasını istediğiniz tüm kodları çağırabilirsiniz
    print("Program başlatılıyor...") 
    main()  # `main` fonksiyonunu çağırıyoruz.
    print("Tüm işlemler başarıyla tamamlandı!")
