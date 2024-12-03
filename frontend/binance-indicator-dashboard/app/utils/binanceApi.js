import axios from 'axios';


const baseUrl = "http://localhost:3000";

export const fetchBinanceCandles = async (symbol = 'BTCUSDT', interval = '1d') => {
    const url = `${baseUrl}/api/fetch-data-bot`;
  
    try {
      // API'ye POST isteği gönderiyoruz
      const response = await axios.post(url, { symbol, interval }, {
        headers: {
          'Content-Type': 'application/json', // JSON formatında veri gönderiyoruz
        },
      });
      console.log(response.data[0].data);
      
      return response.data[0].data;

    } catch (error) {
      console.error('Error fetching Binance candles:', error); // Hataları logluyoruz
      throw error; // Hataları yukarıya fırlatıyoruz
    }
  };

  export function transformCandleData(data) {
    return data.map((candle, index) => ({
      id: index,
      time: new Date(candle[0]).toISOString(),
      open: parseFloat(candle[1]),
      high: parseFloat(candle[2]),
      low: parseFloat(candle[3]),
      close: parseFloat(candle[4]),
      volume: parseFloat(candle[5]),
    }));
  }