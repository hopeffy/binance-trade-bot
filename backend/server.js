require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const botRoutes = require('./src/routes/BotRoutes');
const coinRoutes = require('./src/routes/coinRoutes');
const axios = require('axios');
const cors = require('cors');


const app = express();
const PORT = process.env.PORT; // Server port
const BOT_PORT = process.env.BOT_PORT; // Bot port from .env
const FRONTEND_PORT = process.env.FRONTEND_PORT


// Allow requests from a specific origin
app.use(cors({ origin: 'http://localhost:3001' }));
// Middleware
app.use(express.json());



// Routes
app.use('/api/bot', botRoutes);
//app.use("api/coin", coinRoutes);

const sendRequest = async () => {
  try {
      const response = await axios.post('http://127.0.0.1:5000/run-bot', 
        {
          "symbol": "BTCUSDT",
          "balance": 10000,
          "riskSize": 0.02,
          "strategy": "SMA_Signal_short"
        }
      , {
          headers: {
              'Content-Type': 'application/json'
          }
      });

      console.log('Yanıt:', response.data);
  } catch (error) {
      console.error('Hata oluştu:', error.message);
  }
};

// backende bot üstünden data çekmek için olan method
const fetch_data_bot = async () => {
  try {
      const response = await axios.post('http://127.0.0.1:5000/binance-data', 
        {
          "symbol": "BTCUSDT",
          "interval": "1h"
        }
      , {
          headers: {
              'Content-Type': 'application/json'
          }
      });

      data = response.data;
      return data;
  } catch (error) {
      console.error('Hata oluştu:', error.message);
  }
};

// datayı bot üstünden almak ve frontend kısmında da buna istek atacağız ki data gelsin.
app.post('/api/fetch-data-bot', async (req, res) => {
  try {
      const data = await fetch_data_bot();
      res.status(200).json(data);
  } catch (error) {
      res.status(500).json({ error: error.message });
  }
});

// Server başlatma
app.listen(BOT_PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
  console.log(`Bot is expected to run on port ${BOT_PORT}`);
  sendRequest();
  fetch_data_bot();
  
});

app.listen(FRONTEND_PORT, () => {
  console.log(`Server is running on http://localhost:${FRONTEND_PORT}`);
});