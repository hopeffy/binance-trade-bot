// src/controllers/coinController.js
const { getAllCoins, getCoinById } = require("../models/coinModel");

const getCoins = (req, res) => {
    const coins = getAllCoins();
    res.status(200).json(coins);
};

const getCoin = (req, res) => {
    const { id } = req.params;
    const coin = getCoinById(parseInt(id, 10));
    if (!coin) {
        return res.status(404).json({ error: "Coin not found" });
    }
    res.status(200).json(coin);
};

module.exports = {
    getCoins,
    getCoin,
};
