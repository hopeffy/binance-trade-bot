// src/routes/BotRoutes.js
const express = require('express');
const { sendBotCommand } = require('../controllers/BotController');

const router = express.Router();

router.post('/command', sendBotCommand);

module.exports = router;
