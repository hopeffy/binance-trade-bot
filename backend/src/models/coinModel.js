// src/models/coinModel.js
const coins = [
    { id: 1, name: "Bitcoin", symbol: "BTC", price: 40000 },
    { id: 2, name: "Ethereum", symbol: "ETH", price: 2500 },
    { id: 3, name: "Ripple", symbol: "XRP", price: 0.5 },
];

module.exports = {
    getAllCoins: () => coins,
    getCoinById: (id) => coins.find((coin) => coin.id === id),
};
