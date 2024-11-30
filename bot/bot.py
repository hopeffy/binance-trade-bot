import datetime

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

client = Client(api_key=api_key, api_secret=api_secret)

# fetch historical data with kline
now = datetime.UTC
symbol = "ETHUSDT"
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


def main():
    # Geçmiş verileri çek
    print("Geçmiş veriler çekiliyor...")
    bars = fetch_historical_data(symbol, interval, start_time, end_time)

    # Veriyi DataFrame'e dönüştür
    print("Veriler DataFrame formatına dönüştürülüyor...")
    df = bars_to_data_frame(bars)

    # df yi yazdır
    print(df)

    # yeni bir dataFrame
    close_df = df[['Close']].copy()

    print(close_df)

    # İndikatör parametreleri
    rsi_period = 14
    sma_period = 20
    ema_period = 20
    macd_fast = 12
    macd_slow = 26
    macd_signal_value = 9

    # # İndikatörleri hesapla
    # print("İndikatörler hesaplanıyor...")
    # cl = calculate_indicators(
    #     close_df,
    #     rsi_period=rsi_period,
    #     sma_period=sma_period,
    #     ema_period=ema_period,
    #     macd_fast=macd_fast,
    #     macd_slow=macd_slow,
    #     macd_signal=macd_signal_value
    # )

    # Sinyalleri hesapla
    close_df = rsi_signal(close_df, rsi_period=rsi_period, overbought=70, oversold=30)
    close_df = sma_signal(close_df, timeperiod=sma_period)
    close_df = ema_signal(close_df, timeperiod=ema_period)
    close_df = macd_signal(close_df, fastperiod=macd_fast, slowperiod=macd_slow, signalperiod=macd_signal_value)

    # # Sonuçları görüntüle
    print(close_df.tail(25))


# Bu bölümde çalıştırılmasını istediğiniz kodları ekleyebilirsiniz
if __name__ == "__main__":
    # Burada çalışmasını istediğiniz tüm kodları çağırabilirsiniz
    print("Program başlatılıyor...")
    main()  # `main` fonksiyonunu çağırıyoruz.
    print("Tüm işlemler başarıyla tamamlandı!")
