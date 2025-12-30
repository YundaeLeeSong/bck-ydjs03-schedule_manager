
# Stocks vs. Shorting: A Simple Guide for Alpaca API Users

Imagine you and a friend have apples.

---

## 1. Buying Stocks (“Going Long”)

- **Scenario**: You use your own money to buy an apple today.
- **Expectation**: The apple’s price goes up.
- **Steps**:
  1. **Buy** 1 share at current market price (you spend money).
  2. **Hold** until the price rises.
  3. **Sell** it back (you receive more money if price went up).
- **Profit** = Sell Price − Buy Price

### API Commands
```python
# Buy 1 share
api.submit_order(symbol='XYZ', qty=1, side='buy', type='market', time_in_force='day')

# Later, sell 1 share
api.submit_order(symbol='XYZ', qty=1, side='sell', type='market', time_in_force='day')
```

---

## 2. Shorting Stocks (“Going Short”)

- **Scenario**: You borrow an apple from a friend and sell it now.
- **Expectation**: The apple’s price goes down.
- **Steps**:
  1. **Sell** 1 borrowed share at current price (you receive money).
  2. **Wait** for the price to drop.
  3. **Buy** 1 share at the lower price to return to your friend.
- **Profit** = Sell Price − Buy-to-Cover Price

### API Commands
```python
# Short (sell borrowed share)
api.submit_order(symbol='XYZ', qty=1, side='sell', type='market', time_in_force='day')

# Later, cover (buy back)
api.submit_order(symbol='XYZ', qty=1, side='buy', type='market', time_in_force='day')
```

---

## 3. Day-to-Day Difference

| Action            | Buying (Long)                  | Shorting                             |
|-------------------|--------------------------------|--------------------------------------|
| What You Do       | Pay cash, get share            | Borrow share, sell for cash          |
| Cash Flow Today   | Out −\$100                     | In +\$100                            |
| Future Action     | Sell at higher price           | Buy back at lower price              |
| Profit Example    | \$110 − \$100 = **\$10**       | \$100 − \$90 = **\$10**              |
| If Wrong (Loss)   | Price drops                     | Price rises                          |
| Worst-Case Loss   | 100% of your investment        | Unlimited (price can rise forever)   |

---

## 4. Visual Example

1. **Buying**: You spend \$100, later sell for \$120 → you gain \$20.
2. **Shorting**: You receive \$100 from selling borrowed shares, later buy back at \$80 → you gain \$20.

---

## 5. Checking in Alpaca

After orders:
```python
acct = api.get_account()
print("Long Value: ", acct.long_market_value)
print("Short Value:", acct.short_market_value)
```

---

### Key Takeaway

- **Buy** when you expect a price **rise**.  
- **Short** when you expect a price **fall**.  

Try these simple steps in paper trading and watch your P/L updates in real time—it’ll make the difference clear!









---




# Buying vs Shorting with Alpaca API

Think of **buying** vs **shorting** as mirror-image bets:

---

## A. Buying (“Going Long”)
- **Objective**: Profit when the stock price goes **up**.
- **How**: Use cash to **buy** shares now and **sell** later at a higher price.
- **Profit** = (Sell Price − Buy Price) × Qty
- **API Example**:
  ```python
  # 1. Buy 1 share of AAPL at market
  api.submit_order(
      symbol='AAPL',
      qty=1,
      side='buy',       # going long
      type='market',
      time_in_force='day'
  )
  # 2. Sell 1 share to close long
  api.submit_order(
      symbol='AAPL',
      qty=1,
      side='sell',      # closing the long
      type='market',
      time_in_force='day'
  )
  ```

---

## B. Shorting (“Going Short”)
- **Objective**: Profit when the stock price goes **down**.
- **How**: **Borrow** shares, **sell** them now, then **buy** them back later at a lower price and return them.
- **Profit** = (Sell Price − Buy-to-Cover Price) × Qty
- **API Example**:
  ```python
  # 1. Short 1 share of AAPL at market
  api.submit_order(
      symbol='AAPL',
      qty=1,
      side='sell',      # since you don't own it, this opens a short
      type='market',
      time_in_force='day'
  )
  # 2. Buy 1 share to cover and close the short
  api.submit_order(
      symbol='AAPL',
      qty=1,
      side='buy',       # covering the short
      type='market',
      time_in_force='day'
  )
  ```

---

## C. Numerical Example

| Day | Action            | Price | Cash Flow    | Position         | Realized P/L |
|-----|-------------------|-------|--------------|------------------|--------------|
| 1   | Buy 1 share       | $100  | –$100        | +1 share         | $0           |
| 2   | Sell 1 share      | $110  | +$110        | 0 shares         | +$10         |
| 1   | Short 1 share     | $100  | +$100        | –1 share (short) | $0           |
| 2   | Cover 1 share     | $90   | –$90         | 0 shares short   | +$10         |

- **Long**: Pay $100, receive $110 → **$10 profit**.  
- **Short**: Receive $100, pay $90 → **$10 profit**.

---

## D. Key Differences

| Feature          | Buying (Long)      | Shorting                   |
|------------------|--------------------|----------------------------|
| Market View      | Bullish (↑ price)  | Bearish (↓ price)          |
| Cash Up-Front    | You pay cash       | Broker pays you (borrowed) |
| Risk             | Limited to cash    | **Unlimited** potential    |
| Margin Required  | Cash ≥ cost        | Margin account (min $2,000)|

---

## E. Checking with Alpaca API
```python
acct = api.get_account()
print("Long Market Value: ", acct.long_market_value)
print("Short Market Value:", acct.short_market_value)
```

---

## F. Summary
1. Decide if you’re **bullish** (buy) or **bearish** (short).  
2. Use `side='buy'` to go long; `side='sell'` with no existing position to go short.  
3. Monitor P/L in `acct.unrealized_pl`.  
4. Close with the opposite side: `sell` to close long, `buy` to cover short.

Once you try it in paper trading, the concepts will click!

