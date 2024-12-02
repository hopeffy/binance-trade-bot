// src/controllers/BotController.js
const BotModel = require('../models/BotModel');


const bot = new BotModel(process.env.BOT_PORT); // Botun çalıştığı port

const sendBotCommand = async (req, res) => {
  const { command } = req.body;

  if (!command) {
    return res.status(400).json({ error: 'Command is required' });
  }

  try {
    const response = await bot.sendCommand(command);
    res.status(200).json({ success: true, data: response });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
};

module.exports = { sendBotCommand };
