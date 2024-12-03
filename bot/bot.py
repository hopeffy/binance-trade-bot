import json
from datetime import datetime, timedelta

import pandas as pd
import os

import requests
from binance.client import Client
import talib
from flask import Flask, request, jsonify

app = Flask(__name__)

# Reading APIs from environment variables to keep them secure
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
start_date = datetime.now() - timedelta(days=120)
# Indicator values per coin
indicators = pd.DataFrame(
    columns=["Symbol", "RSI_overbought", "RSI_oversold", "RSI_interval", "SMA_short", "SMA_long", "EMA_short",
             "EMA_long", "MACD_fast", "MACD_slow", "MACD_signal", "interval", "start_time", "end_time"])
indicators.loc[0] = ["BTCUSDT", 70, 30, 14, 10, 30, 9, 21, 12, 26, 9, "1d", f'{start_date}', f'{datetime.now()}']
indicators.loc[1] = ["ETHUSDT", 70, 30, 14, 10, 30, 9, 21, 12, 26, 9, "1d", f'{start_date}', f'{datetime.now()}']
indicators.loc[2] = ["BNBUSDT", 70, 30, 14, 10, 30, 9, 21, 12, 26, 9, "1d", f'{start_date}', f'{datetime.now()}']
indicators.loc[3] = ["ADAUSDT", 70, 30, 14, 10, 30, 9, 21, 12, 26, 9, "1d", f'{start_date}', f'{datetime.now()}']
indicators.loc[4] = ["XRPUSDT", 70, 30, 14, 10, 30, 9, 21, 12, 26, 9, "1d", f'{start_date}', f'{datetime.now()}']
indicators.loc[5] = ["DOGEUSDT", 70, 30, 14, 10, 30, 9, 21, 12, 26, 9, "1d", f'{start_date}', f'{datetime.now()}']

# # Trading states
# positions = pd.DataFrame(columns=["Symbol", "Entry Price", "Position", "Position Size"])
# positions.loc[0] = ["BTCUSDT", 0, False, 0]
# positions.loc[1] = ["ETHUSDT", 0, False, 0]
# positions.loc[2] = ["BNBUSDT", 0, False, 0]
# positions.loc[3] = ["ADAUSDT", 0, False, 0]
# positions.loc[4] = ["XRPUSDT", 0, False, 0]
# positions.loc[5] = ["DOGEUSDT", 0, False, 0]


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
start_time = f'{start_date}'
end_time = f'{datetime.now()}'


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
    columns = ["Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time"]
    df = pd.DataFrame(bars, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ])
    df["Open Time"] = pd.to_datetime(df["Open Time"], unit="ms")
    df["Close Time"] = pd.to_datetime(df["Close Time"], unit="ms")
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
    rsi_column_name = 'RSI'
    df[rsi_column_name] = rsi_column  # RSI değerlerini dataframe'e ekle

    # Varsayılan sinyal sütunu
    signal_column_name = 'RSI_Signal'
    df[signal_column_name] = 0  # Varsayılan sinyal değeri

    # Koşullu sinyaller
    df.loc[(df[rsi_column_name] > oversold) & (
                df[rsi_column_name].shift(1) <= oversold), signal_column_name] = 1  # Alış sinyali
    df.loc[(df[rsi_column_name] < overbought) & (
                df[rsi_column_name].shift(1) >= overbought), signal_column_name] = -1  # Satış sinyali

    return df


def calculate_sma(df, timeperiod):
    """SMA hesaplama."""
    close_prices = df['Close']
    df['SMA_'f'{timeperiod}'] = talib.SMA(close_prices, timeperiod=timeperiod)
    return df['SMA_'f'{timeperiod}']


def sma_signal(df, timeperiod, short_or_long: str):
    """
    SMA sinyal hesaplama.
    - Fiyat SMA'nın üzerindeyse ve önceki mumda SMA'nın altındaysa alış sinyali (1).
    - Fiyat SMA'nın altındaysa ve önceki mumda SMA'nın üzerindeyse satış sinyali (-1).
    """
    # SMA hesaplama
    sma_column = calculate_sma(df, timeperiod=timeperiod)
    sma_column_name = f'SMA_{short_or_long}'
    df[sma_column_name] = sma_column  # SMA'yı dataframe'e ekle

    # Varsayılan sinyal sütunu
    signal_column_name = f'SMA_Signal_{short_or_long}'
    df[signal_column_name] = 0  # Varsayılan sinyal değeri

    # Koşullu sinyaller
    df.loc[(df['Close'] > df[sma_column_name]) & (
                df['Close'].shift(1) < df[sma_column_name].shift(1)), signal_column_name] = 1
    df.loc[(df['Close'] < df[sma_column_name]) & (
                df['Close'].shift(1) > df[sma_column_name].shift(1)), signal_column_name] = -1

    return df


def calculate_ema(df, timeperiod):
    """EMA hesaplama."""
    df['EMA_'f'{timeperiod}'] = talib.EMA(df['Close'], timeperiod=timeperiod)
    return df['EMA_'f'{timeperiod}']


def ema_signal(df, timeperiod, short_or_long: str):
    """
    EMA sinyal hesaplama.
    - Fiyat EMA'nın üzerindeyse ve önceki mumda EMA'nın altındaysa alış sinyali (1).
    - Fiyat EMA'nın altındaysa ve önceki mumda EMA'nın üzerindeyse satış sinyali (-1).
    """
    # EMA hesaplama
    ema_column = calculate_ema(df, timeperiod=timeperiod)
    ema_column_name = f'EMA_{short_or_long}'
    df[ema_column_name] = ema_column  # EMA'yı dataframe'e ekle

    # Varsayılan sinyal sütunu
    signal_column_name = f'EMA_Signal_{short_or_long}'
    df[signal_column_name] = 0  # Varsayılan sinyal değeri

    # Koşullu sinyaller
    df.loc[(df['Close'] > df[ema_column_name]) & (
                df['Close'].shift(1) < df[ema_column_name].shift(1)), signal_column_name] = 1
    df.loc[(df['Close'] < df[ema_column_name]) & (
                df['Close'].shift(1) > df[ema_column_name].shift(1)), signal_column_name] = -1

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
    df.loc[(df['MACD'] > df['MACD_Signal_Line']) & (
                df['MACD'].shift(1) < df['MACD_Signal_Line'].shift(1)), signal_column_name] = 1
    df.loc[(df['MACD'] < df['MACD_Signal_Line']) & (
                df['MACD'].shift(1) > df['MACD_Signal_Line'].shift(1)), signal_column_name] = -1

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
        bars = fetch_historical_data(indicators["Symbol"][i], indicators["interval"][i], indicators["start_time"][i],
                                     indicators["end_time"][i])
        df = bars_to_data_frame(bars)
        df = rsi_signal(df, rsi_period=indicators["RSI_interval"][i], overbought=indicators["RSI_overbought"][i],
                        oversold=indicators["RSI_oversold"][i])
        df = sma_signal(df, indicators["SMA_short"][i], short_or_long="short")
        df = sma_signal(df, indicators["SMA_long"][i], short_or_long="long")
        df = ema_signal(df, indicators["EMA_short"][i], short_or_long="short")
        df = ema_signal(df, indicators["EMA_long"][i], short_or_long="long")
        df = macd_signal(df, fastperiod=indicators["MACD_fast"][i], slowperiod=indicators["MACD_slow"][i],
                         signalperiod=indicators["MACD_signal"][i])

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


def get_symbol_index(symbol, positions, position_value):
    index_list = positions[positions['Symbol'] == symbol]
    index_list["Position"] = position_value
    return index_list


# Calculating tp and sl prices
def take_profit(symbol, positions=pd.DataFrame):
    df = f'{symbol}_df'
    entry_price = positions.loc[positions["Symbol"] == symbol, "Entry Price"]
    tp_price = entry_price * 1.02
    return tp_price


# def stop_loss(symbol, position):
#     df= f'{symbol}_df'
#     entry_price = positions.loc[positions["Symbol"] == symbol, "Entry Price"]
#     sl_price = entry_price * 0.98
#     return sl_price

# Trading actions. Returns true if there is need to SELL
# def tp_sl_actions(symbol, positions):
#     tp_price = take_profit(symbol, positions)
#     sl_price = stop_loss(symbol, positions)
#     df: pd.DataFrame = symbol_to_df(symbol=symbol)
#     if not df.empty and df.iloc[-1]["Close"] >= tp_price:
#         return True
#
#     elif not df.empty and df.iloc[-1]["Close"] <= sl_price:
#         return True
#
#     return False

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


def backtest_V2(df, risk_size, balance, strategy, symbol):
    sl_count = 0
    tp_count = 0
    for i, row in df.iterrows():
        low = row["Low"]
        high = row["High"]
        karar = row[strategy]
        curr_price = row["Close"]
        stop_level = curr_price * (1 - risk_size)
        tp_level = curr_price * (1 + risk_size)
        coin_amount = 0
        is_buy = False
        if karar == 1:
            is_buy = True
            coin_amount = balance / curr_price
            if is_buy:
                if low < stop_level:
                    balance = balance - ((curr_price - stop_level) * coin_amount)
                    is_buy = False
                    sl_count += 1
                elif high > tp_level:
                    balance = balance + ((tp_level - curr_price) * coin_amount)
                    is_buy = False
                    tp_count += 1
    result = pd.DataFrame({
        "Symbol": [symbol],  # Wrap scalar in a list
        "SL_Count": [sl_count],  # Wrap scalar in a list
        "TP_Count": [tp_count],  # Wrap scalar in a list
        "Result": [balance]  # Wrap scalar in a list
    })
    return result





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

    result_BTC = backtest_V2(df=BTC_df, balance=10000, risk_size=0.02, strategy="SMA_Signal_short",
                         symbol="BTCUSDT")
    result_ETH = backtest_V2(df=ETH_df, balance=1000, risk_size=0.02, strategy="RSI_Signal",
                         symbol="ETHUSDT")
    result_BNB = backtest_V2(df=ETH_df, balance=1000, risk_size=0.02, strategy="RSI_Signal",
                         symbol="BNBUSDT")
    result_ADA = backtest_V2(df=ETH_df, balance=1000, risk_size=0.02, strategy="RSI_Signal",
                         symbol="ADAUSDT")
    result_XRP = backtest_V2(df=ETH_df, balance=1000, risk_size=0.02, strategy="RSI_Signal",
                         symbol="XRPUSDT")
    result_DOGE = backtest_V2(df=ETH_df, balance=1000, risk_size=0.02, strategy="RSI_Signal",
                         symbol="DOGEUSDT")

    print(result_BTC)

    bars = fetch_historical_data(symbol="BTCUSDT", interval=interval, start_time=start_time, end_time=end_time)
    df = bars_to_data_frame(bars)
    print(df)

    print("All backtests completed successfully!")

def transform_to_apexcharts_format(df):
    result = [
        {
            "name": "Candle Data",
            "data": [
                {
                    "x": row["Open Time"],  # X ekseni için zaman bilgisi
                    "y": [row["Open"], row["High"], row["Low"], row["Close"], row["Volume"]]  # Y ekseni için [open, high, low, close, volume]
                }
                for _, row in df.iterrows()
            ]
        }
    ]
    return result


@app.route('/run-bot', methods=['POST'])
def run_bot():
    # You can process inputs from the request if needed
    data = request.json
    symbol = data.get('symbol')
    balance = data.get('balance')  # Default to 10000 if not provided
    risk_size = data.get('riskSize')  # Default to 0.02 if not provided
    strategy = data.get('strategy')

    result_BTC = backtest_V2(df=BTC_df, balance=balance, risk_size=risk_size, strategy=strategy, symbol=symbol)
    return jsonify({"result_BTC": result_BTC.to_dict(orient='records')})

@app.route('/binance-data', methods=['POST'])
def binance_data():
    """
    Binance'ten veri çeker ve backend'e gönderir.
    """
    try:
        data = request.json
        symbol = data.get('symbol')
        interval = data.get('interval')
        bars = fetch_historical_data(symbol=symbol, interval=interval, start_time=start_time, end_time=end_time)
        df = bars_to_data_frame(bars)
        json_data = df.to_json(orient="records")
        resultChart = transform_to_apexcharts_format(df)
        return jsonify(resultChart)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Bu bölümde çalıştırılmasını istediğiniz kodları ekleyebilirsiniz
if __name__ == "__main__":
    # Burada çalışmasını istediğiniz tüm kodları çağırabilirsiniz
    print("Program başlatılıyor...")
    # main()  # `main` fonksiyonunu çağırıyoruz.
    app.run(host='0.0.0.0', port=5000, debug=True)
