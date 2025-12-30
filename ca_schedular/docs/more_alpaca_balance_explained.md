
# More Detailed Explanation of Your Alpaca Balance Sheet

Let’s start from the very beginning and build up each concept step by step, with simple language and examples. Think of your Alpaca account like a checking account plus a small “loan closet” where you can borrow extra money to trade—this borrowing is called **margin**.

---

## 1. Cash vs. Equity

### 💵 Cash
- **What it is:** The actual dollars sitting in your account.  
- **Example:** If you’ve deposited $1,000 from your bank, your Cash balance starts at $1,000.

### ⚖️ Equity
- **What it is:** Your **net worth** inside Alpaca. It’s simply  
  ```
  Equity = Cash + Value of your positions (stocks/crypto)
  ```
- **Example:**
  - Cash = $1,000  
  - You buy $600 worth of AAPL → Cash drops to $400, Positions = $600.  
  - Equity = $400 + $600 = $1,000 (your net hasn’t changed).

---

## 2. Buying Power

Buying power is **how much you’re allowed to spend today** on new trades.

### 2.1. Cash Buying Power (Non-Marginable)
- You can only spend **settled cash**. Stocks take 2 business days (T+2) to settle, so if you sell shares today, you can’t instantly spend that money.

### 2.2. Reg T Buying Power (Margin Buying Power)
- By U.S. Regulation T, a broker can lend you up to **50% extra** on marginable securities.
- **Formula:**
  ```
  Reg T Buying Power = 2 × (settled cash)
  ```
- **Example:**
  - Settled cash = $1,000 → Reg T Buying Power = $2,000.  
  - You could buy $2,000 of stock by putting up your $1,000 and borrowing $1,000 from Alpaca.

### 2.3. Effective Buying Power
- This is simply the actual amount you can spend right now, taking into account any margin you’ve already used or holds on your account. In a simple account with no open trades, **Effective Buying Power = Reg T Buying Power**.

---

## 3. Margin in Detail

### 🤝 What Is Margin?
- **Margin** is borrowing money from Alpaca to buy more stock than you could with your cash alone.

### Why Use Margin?
- To **amplify gains** if you’re confident a stock will go up.  
- **Risk:** losses are also amplified—and if your equity drops too far, you get a **margin call**.

### Key Margin Metrics in Your Alpaca Statement

| Metric                | What It Means                                                                                   |
|-----------------------|--------------------------------------------------------------------------------------------------|
| **Initial Margin**    | The dollar amount Alpaca has set aside (reserved) to cover your current borrowed positions.     |
| **Maintenance Margin**| The minimum equity you must keep in your account after you’ve borrowed to avoid a margin call.   |
| **SMA**               | “Special Memorandum Account” credit you earn when you sell at a profit; it can boost your buying power temporarily. |

---

## 4. Putting It All Together: A Walk-Through Example

1. **You deposit $1,000** in cash.  
   - Cash = $1,000  
   - Equity = $1,000  
   - Reg T Buying Power = $2,000  

2. **You buy $1,500 of stock on margin** (you put up $750, Alpaca lends $750).  
   - Cash spent: $1,500 → Cash goes from $1,000 to **–$500** (you owe Alpaca!)  
   - Margin loan: $750  
   - Positions value: $1,500  
   - Equity = Cash + Positions = –$500 + $1,500 = $1,000  
   - Initial Margin reserved: $750  
   - Maintenance Margin, say 25% of $1,500 = $375.

3. **Your stock drops 20%** (Positions now $1,200).  
   - Equity = –$500 + $1,200 = $700  
   - Maintenance requirement = 25% × $1,200 = $300 → still above required.

4. **If stock drops further** so equity falls below $300, Alpaca issues a **margin call**:  
   - You must deposit cash or sell shares to bring equity back above maintenance.

---

## 5. Why Your Statement Looked Weird

- **Cash negative** means you borrowed on margin.  
- **Reg T Buying Power** dropped to show how much extra you can still borrow.  
- **Initial & Maintenance Margins** show how much Alpaca has “reserved” and what equity you must maintain.  
- **Equity** remained near your original deposit (minus any P/L) because it’s net worth: cash + positions.

---

### Bottom Line

1. **Cash** = what you deposited (can go negative if you borrow).  
2. **Equity** = your net worth in the account (cash + positions).  
3. **Buying Power** = how much you can spend now (cash-only vs. including margin).  
4. **Margin** = borrowed money; initial & maintenance margins keep you within safe leverage limits.

Feel free to ask follow-up questions or request more examples on any specific line item!
