// src/models/BotModel.js
require('dotenv').config();

const axios = require('axios');

class BotModel {
  constructor() {
    this.port = process.env.BOT_PORT;
    this.baseUrl = `http://localhost:${this.port}`;
  }

  async sendCommand(command) {
    try {
      const response = await axios.post(`${this.baseUrl}/command`, { command });
      return response.data;
    } catch (error) {
      console.error('Error communicating with the bot:', error.message);
      throw new Error('Bot communication failed');
    }
  }
}

module.exports = BotModel;
