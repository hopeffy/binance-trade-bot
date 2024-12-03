// Placeholder for any model logic, e.g., data validation
class BotRequest {
  constructor(symbol, balance, riskSize, strategy) {
      this.symbol = symbol;
      this.balance = balance;
      this.riskSize = riskSize;
      this.strategy = strategy;
  }

  isValid() {
      // Validate input data
      return this.symbol && this.balance > 0 && this.riskSize > 0 && this.strategy;
  }
}

module.exports = BotRequest;