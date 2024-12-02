require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const botRoutes = require('./src/routes/BotRoutes');
const coinRoutes = require('./src/routes/coinRoutes');

const app = express();
const PORT = process.env.PORT || 3000; // Server port
const BOT_PORT = process.env.BOT_PORT; // Bot port from .env
const FRONTEND_PORT = process.env.FRONTEND_PORT

// Middleware
app.use(bodyParser.json());

// Routes
app.use('/api/bot', botRoutes);
app.use("api/coin", coinRoutes)

// Server başlatma
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
  console.log(`Bot is expected to run on port ${BOT_PORT}`);
});

app.listen(FRONTEND_PORT, () => {
  console.log(`Server is running on http://localhost:${FRONTEND_PORT}`);
});