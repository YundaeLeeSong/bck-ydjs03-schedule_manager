
# How is Cash Withdrawable Decided in Alpaca?

**Cash Withdrawable** in Alpaca (or any brokerage) represents the amount of cash you can *actually* transfer out of your account at that moment. It’s often **less than your total cash balance** because of several temporary restrictions or settlement rules.

---

## 🔍 How is it Decided?

The **Cash Withdrawable** amount is based on:

### 1. Settlement Period
- In the U.S. stock market, trades follow the **T+2 rule** (Trade date + 2 business days to settle).
- This means if you sell a stock today, the proceeds won't be *fully available to withdraw* until 2 business days later.
- Until then, it stays in your "Cash" but is **not withdrawable**.

### 2. Pending Orders or Holds
- If you have:
  - **Open buy/sell orders**
  - **Pending crypto transactions**
  - **ACH deposits on hold**
- Those funds are marked as **non-withdrawable** until cleared.

### 3. Margin Activity
- If you’re using **margin** (borrowing money to buy stocks), the broker may **restrict** how much of your cash you can withdraw to ensure they’re covered.
- Even without using margin intentionally, **settlement issues** can cause margin to be "used" temporarily.

### 4. Recent Deposits
- New deposits (e.g., via ACH) might be **held for several days** until they clear from your bank.
- These amounts show in your cash, but not as withdrawable yet.

### 5. Crypto Trading Limits
- Crypto trades often settle faster (instant or T+1), but **Alpaca may restrict withdrawals** if you bought crypto recently or your account has crypto-related limits.

---

## 🧠 Quick Example

Let’s say you:
- Deposited $10,000 today → **Not withdrawable yet** (ACH hold)
- Sold $2,000 worth of stock today → **Not withdrawable until T+2**
- Had $1,000 left in cash from earlier → **Only this is withdrawable**

So your total **cash** might be $13,000, but your **withdrawable cash** is just $1,000.

---
