from datetime import datetime

import pandas as pd
import os
from binance.client import Client
import talib

# reading env file

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
    - RSI oversold seviyesini geçerse ve önceki mumda altında kalmışsa alış sinyali (1).
    - RSI overbought seviyesinin altına düşerse ve önceki mumda üstünde kalmışsa satış sinyali (-1).
    """
    # RSI hesaplama
    rsi_column = calculate_rsi(df=df, timeperiod=rsi_period)
    rsi_column_name = f'RSI_{rsi_period}'
    df[rsi_column_name] = rsi_column  # RSI değerlerini dataframe'e ekle

    # Varsayılan sinyal sütunu
    signal_column_name = f'RSI_Signal_{rsi_period}'
    df[signal_column_name] = 0  # Varsayılan sinyal değeri

    # Koşullu sinyaller
    df.loc[(df[rsi_column_name] > oversold) & (df[rsi_column_name].shift(1) <= oversold), signal_column_name] = 1  # Alış sinyali
    df.loc[(df[rsi_column_name] < overbought) & (df[rsi_column_name].shift(1) >= overbought), signal_column_name] = -1  # Satış sinyali

    return df



def calculate_sma(df, timeperiod):
    """SMA hesaplama."""
    close_prices = df['Close']
    df['SMA_'f'{timeperiod}'] = talib.SMA(close_prices, timeperiod=timeperiod)
    return df['SMA_'f'{timeperiod}']


def sma_signal(df, timeperiod):
    """
    SMA sinyal hesaplama.
    - Fiyat SMA'nın üzerindeyse ve önceki mumda SMA'nın altındaysa alış sinyali (1).
    - Fiyat SMA'nın altındaysa ve önceki mumda SMA'nın üzerindeyse satış sinyali (-1).
    """
    # SMA hesaplama
    sma_column = calculate_sma(df, timeperiod=timeperiod)
    sma_column_name = f'SMA_{timeperiod}'
    df[sma_column_name] = sma_column  # SMA'yı dataframe'e ekle
    
    # Varsayılan sinyal sütunu
    signal_column_name = f'SMA_Signal_{timeperiod}'
    df[signal_column_name] = 0  # Varsayılan sinyal değeri
    
    # Koşullu sinyaller
    df.loc[(df['Close'] > df[sma_column_name]) & (df['Close'].shift(1) < df[sma_column_name].shift(1)), signal_column_name] = 1
    df.loc[(df['Close'] < df[sma_column_name]) & (df['Close'].shift(1) > df[sma_column_name].shift(1)), signal_column_name] = -1
    
    return df



def calculate_ema(df, timeperiod):
    """EMA hesaplama."""
    df['EMA_'f'{timeperiod}'] = talib.EMA(df['Close'], timeperiod=timeperiod)
    return df['EMA_'f'{timeperiod}']


def ema_signal(df, timeperiod):
    """
    EMA sinyal hesaplama.
    - Fiyat EMA'nın üzerindeyse ve önceki mumda EMA'nın altındaysa alış sinyali (1).
    - Fiyat EMA'nın altındaysa ve önceki mumda EMA'nın üzerindeyse satış sinyali (-1).
    """
    # EMA hesaplama
    ema_column = calculate_ema(df, timeperiod=timeperiod)
    ema_column_name = f'EMA_{timeperiod}'
    df[ema_column_name] = ema_column  # EMA'yı dataframe'e ekle
    
    # Varsayılan sinyal sütunu
    signal_column_name = f'EMA_Signal_{timeperiod}'
    df[signal_column_name] = 0  # Varsayılan sinyal değeri
    
    # Koşullu sinyaller
    df.loc[(df['Close'] > df[ema_column_name]) & (df['Close'].shift(1) < df[ema_column_name].shift(1)), signal_column_name] = 1
    df.loc[(df['Close'] < df[ema_column_name]) & (df['Close'].shift(1) > df[ema_column_name].shift(1)), signal_column_name] = -1
    
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
    - MACD > MACD Signal ve önceki mumda MACD < MACD Signal: Alış sinyali.
    - MACD < MACD Signal ve önceki mumda MACD > MACD Signal: Satış sinyali.
    """
    # MACD hesaplama
    macd, macd_signal, macd_hist = calculate_macd(df, fastperiod, slowperiod, signalperiod)
    
    # MACD ve MACD Signal sütunlarını dataframe'e ekle
    df['MACD'] = macd
    df['MACD_Signal_Line'] = macd_signal
    
    # Varsayılan sinyal sütunu
    signal_column_name = 'MACD_Signal'
    df[signal_column_name] = 0  # Varsayılan sinyal değeri
    
    # Koşullu sinyaller
    df.loc[(df['MACD'] > df['MACD_Signal_Line']) & (df['MACD'].shift(1) < df['MACD_Signal_Line'].shift(1)), signal_column_name] = 1
    df.loc[(df['MACD'] < df['MACD_Signal_Line']) & (df['MACD'].shift(1) > df['MACD_Signal_Line'].shift(1)), signal_column_name] = -1
    
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
    df: pd.DataFrame = symbol_to_df(symbol=symbol)
    if df.iloc[-1]["Close"] >= tp_price:
        return True
        
    elif df["Close"] <= sl_price:
        return True

    return False

def symbol_to_df(symbol):
    if symbol == "BTCUSDT":
        return BTC_df
    elif symbol == "ETHUSDT":
        return ETH_df
    elif symbol == "BNBUSDT":
        return BNB_df
    elif symbol == "ADAUSDT":
        return ADA_df
    elif symbol == "XRPUSDT":
        return XRP_df
    elif symbol == "DOGEUSDT":
        return DOGE_df

def take_decision(symbol, symbol_df: pd.DataFrame, positions_df: pd.DataFrame, indicators: pd.DataFrame):
    df = pd.DataFrame()
    df= symbol_df
    rsi_signal_value = df.iloc[-1].filter(regex="^RSI_Signal").values[0]
    sma_signal_short_value = df.iloc[-1].filter(regex="^SMA_Signal").values[0]
    sma_signal_long_value = df.iloc[-1].filter(regex="^SMA_Signal").values[0]
    ema_signal_short_value = df.iloc[-1].filter(regex="^EMA_Signal").values[0]
    ema_signal_long_value = df.iloc[-1].filter(regex="^EMA_Signal").values[0]
    macd_signal_value = df.iloc[-1].filter(regex="^MACD_Signal").values[0]

    close_price = df.iloc[-1]["Close"]


    # Aggregated decision-making
    buy_signals = 0
    sell_signals = 0
    hold_signals = 0
    total_signal = 0

    # Count buy/sell signals from all indicators
    if rsi_signal_value == 1:
        buy_signals += 1
    elif rsi_signal_value == -1:
        sell_signals += 1
    elif rsi_signal_value == 0:
        hold_signals += 1

    if sma_signal_short_value == 1 or sma_signal_long_value == 1:
        buy_signals += 1
    elif sma_signal_short_value == -1 or sma_signal_long_value == -1:
        sell_signals += 1

    if ema_signal_short_value == 1 or ema_signal_long_value == 1:
        buy_signals += 1
    elif ema_signal_short_value == -1 or ema_signal_long_value == -1:
        sell_signals += 1

    if macd_signal_value == 1:
        buy_signals += 1
    elif macd_signal_value == -1:
        sell_signals += 1

    total_signal = buy_signals + sell_signals + hold_signals
    buy_ratio = buy_signals/total_signal
    sell_ratio = sell_signals/total_signal
    hold_signals = hold_signals/total_signal
    idx = 0
    for i in range(len(positions)):
        if not positions.empty() & positions.loc[i, "Symbol"] == symbol:
            idx = i
            break
  

    # Pozisyon güncellemesi
    if buy_ratio > sell_ratio and buy_ratio > hold_signals:
        # Buy sinyali
        if symbol in positions_df["Symbol"].values:
            positions.loc[idx, "Position"] = True
            return "BUY"
    elif (sell_ratio > hold_signals and sell_ratio > buy_ratio) or tp_sl_actions(symbol_to_df(symbol), positions):
        # Sell sinyali
        if symbol in positions_df["Symbol"].values:
            # Mevcut pozisyonu kapat
            positions.loc[idx, "Position"] = False
            return "SELL"
    else:
        # Hold (Hiçbir şey yapma)
        return "HOLD"




def backtest(symbol, initial_balance=10000, trade_size=0.1):
    symbol_df = symbol_to_df(symbol)
    balance = initial_balance
    position_size = 0  # Pozisyon büyüklüğü
    entry_price = 0
    trades = 0

    # DataFrame boyunca iterasyon
    for i in range(1, len(symbol_df)):
        # O andaki karar
        current_df = symbol_df.iloc[:i + 1]  # Mevcut veri seti
        decision = take_decision(current_df, symbol_df=symbol_df, indicators=indicators, positions_df=positions)  # Kararı al
        current_price = symbol_df.iloc[i]["Close"]

        if decision == "BUY" and position_size == 0:
            # Pozisyon aç
            position_size = (balance * trade_size) / current_price
            entry_price = current_price
            balance -= position_size * entry_price
            trades += 1
            print(f"BUY: {position_size:.4f} BTC at {entry_price:.2f}")

        elif decision == "SELL" and position_size > 0:
            # Pozisyon kapat
            balance += position_size * current_price
            profit = (current_price - entry_price) * position_size
            print(f"SELL: {position_size:.4f} BTC at {current_price:.2f}, Profit: {profit:.2f}")
            position = 0
            entry_price = 0
            trades += 1

    # Kalan pozisyonu kapat
    if position > 0:
        balance += position_size * symbol_df.iloc[-1]["Close"]
        print(f"Closing remaining position at {symbol_df.iloc[-1]['Close']:.2f}")

    # Backtest sonuçları
    profit_loss = balance - initial_balance
    print(f"Final Balance: ${balance:.2f}, Profit/Loss: ${profit_loss:.2f}, Total Trades: {trades}")
    return {
        "Final Balance": balance,
        "Profit/Loss": profit_loss,
        "Total Trades": trades
    }




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



    results = []  # Store backtest results

    # Loop through each symbol and run the backtest
    # for i in range(len(indicators)):
    #     symbol = indicators["Symbol"][i]
    #     interval = indicators["interval"][i]
    #
    #     print(f"Running backtest for {symbol} ({interval})...")
    #     result = backtest(symbol=symbol, symbol_df=BTC_df, initial_balance=10000, trade_size=0.1)  # Run the backtest
    #     results.append(result)  # Save the result for later analysis
    #
    # # Display the backtest summary
    # print("\nBacktest Summary:")
    # for result in results:
    #     print(result)

    result = backtest(symbol="BTCUSDT", initial_balance=10000, trade_size=0.1)  # Run the backtest
    with open("backtest_results.txt", "w") as file:
        file.write(str(result))

    print("All backtests completed successfully!")

    

    


# Bu bölümde çalıştırılmasını istediğiniz kodları ekleyebilirsiniz
if __name__ == "__main__":
    # Burada çalışmasını istediğiniz tüm kodları çağırabilirsiniz
    print("Program başlatılıyor...") 
    main()  # `main` fonksiyonunu çağırıyoruz.
    print("Tüm işlemler başarıyla tamamlandı!")
