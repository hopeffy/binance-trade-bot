// src/routes/BotRoutes.js
const express = require('express');
const { runBot } = require('../controllers/BotController');


const router = express.Router();
router.post('/run-bot', runBot);


module.exports = router;
