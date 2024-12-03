"use client";

import { useState, useEffect } from 'react';
import { fetchBinanceCandles } from '../app/utils/binanceApi';
import CandleChart from '../app/components/CandleChart';

const Home = () => {
  const [candles, setCandles] = useState([]);
  const [indicator, setIndicator] = useState('');
  const [value, setValue] = useState('');

  const transformCandleData = (data) => {
    return data.map((candle, index) => ({
      id: index,
      open: candle.Open,
      high: candle.High,
      low: candle.Low,
      close: candle.Close,
      volume: candle.Volume,
    }));
  };

    // Verileri yüklemek için loadCandles fonksiyonu
  const loadCandles = async () => {
    try {
      const data = await fetchBinanceCandles(); // API'den veri al
      setCandles(data); // Veriyi state'e kaydet
    } catch (error) {
      console.error("Error loading candles:", error); // Hata loglaması
    }
  };

  // İlk render'da verileri yükle
  useEffect(() => {
    loadCandles();
  }, []);

  useEffect(() => {
    const loadCandles = async () => {
      const data = await fetchBinanceCandles();
      setCandles(data);
    };
    loadCandles();
  }, []);

  const handleIndicatorChange = (e) => setIndicator(e.target.value);
  const handleValueChange = (e) => setValue(e.target.value);

  return (
    <div style={{ padding: "20px" }}>
      <h1>Binance Candle Chart</h1>
      <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
        <CandleChart data={candles} />
        <div>
          <label>Indicator:</label>
          <select value={indicator} onChange={handleIndicatorChange}>
            <option value="">Select</option>
            <option value="sma">SMA_Signal_short</option>
            <option value="sma">SMA_Signal_long</option>
            <option value="ema">EMA_short</option>
            <option value="ema">EMA_long</option>
            <option value="ema">RSI</option>
            <option value="ema">MACD</option>
          </select>
          <br />
          <label>Value:</label>
          <input
            type="number"
            value={value}
            onChange={handleValueChange}
            placeholder="Enter value"
          />
        </div>
      </div>
    </div>
  );
};

export default Home;
