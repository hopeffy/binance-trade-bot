// src/routes/coinRoutes.js
const express = require("express");
const { getCoins, getCoin } = require("../controllers/coinController");

const router = express.Router();

// GET /coins - Tüm coinleri getir
router.get("/coins", getCoins);

// GET /coins/:id - Belirli bir coin bilgisi getir
router.get("/coins/:id", getCoin);

module.exports = router;
