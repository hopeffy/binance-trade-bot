// src/controllers/BotController.js
const BotRequest = require('../models/BotModel');
const BotModel = require('../models/BotModel');



const bot = new BotModel(process.env.BOT_PORT); // Botun çalıştığı port

const runBot = async (req, res) => {
  
  try {
    const { symbol, balance, riskSize, strategy } = req.body;
    // Validate incoming data
    const botRequest = new BotRequest("BTCUSDT",10000,0.02,"SMA_Signal_short");
    if (!botRequest.isValid()) {
        return res.status(400).json({ error: 'Invalid input data' });
    }

    // Forward request to Python bot
    const response = await axios.post('http://127.0.0.1:5000/run-bot', botRequest.body);
    console.log(response);
    
    res.status(200).json(response.data);
} catch (error) {
    console.error('Error communicating with Python bot:', error);
    res.status(500).send('Error communicating with Python bot');
    console.log(error);
    
}
};



module.exports = { runBot};
