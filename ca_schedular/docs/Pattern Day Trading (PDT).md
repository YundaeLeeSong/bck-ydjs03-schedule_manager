# Pattern Day Trading (PDT) Explained

This document walks through how Alpaca (and FINRA) count day-trades—and why only **round-trips** (buy **and** sell in the same day) trigger the PDT block.

---

## 1. Core Definitions

1. **Day-trade (round-trip):**  
   “A day trade consists of buying (or selling short) and then selling (or buying to cover) the same security on the same calendar day.”

2. **Pattern Day-Trader (PDT):**  
   Any margin account that executes **four** or more day-trades within **five** business days, provided those day-trades represent more than 6% of total trades in that window.

3. **PDT Protection:**  
   Alpaca rejects any sell (exit) order that **would** make you exceed **3** day-trades in the rolling 5-day window if your account equity is under \$25,000.

---

## 2. FINRA’s Canonical Examples

Let’s see how FINRA itself counts day-trades in a single day (all on “ABC”):

| Time  | Action       | Qty  | Day-Trades So Far |
|-------|--------------|------|-------------------|
| 09:30 | Buy 250 ABC  | +250 | 0                 |
| 09:31 | Buy 250 ABC  | +250 | 0                 |
| 13:00 | Sell 500 ABC | –500 | 1 (day-trade)     |

> **Result:** 1 day-trade

---

| Time  | Action       | Qty  | Day-Trades So Far |
|-------|--------------|------|-------------------|
| 09:30 | Buy 100 ABC  | +100 | 0                 |
| 09:31 | Sell 100 ABC | –100 | 1                 |
| 09:32 | Buy 100 ABC  | +100 | 1                 |
| 13:00 | Sell 100 ABC | –100 | 2                 |

> **Result:** 2 day-trades

---

## 3. When **Buys** or **Sells** Alone Don’t Count

- **Pure Buys:** No exits today → **0** day-trades  
- **Pure Sells** (of old shares): Selling shares held overnight → **0** new day-trades

---

## 4. Custom AMD Scenarios

1. **Scenario A: Only Buys**  
   - 10 AM: Buy 1 AMD  
   - 11 AM: Buy 1 AMD  
   → **Day-trades:** 0

2. **Scenario B: Buy → Sell Later (1 round-trip)**  
   - 10 AM: Buy 2 AMD  
   - 2 PM: Sell 2 AMD  
   → **Day-trades:** 1

3. **Scenario C: Two Round-Trips**  
   - 9:30 AM: Buy 1 AMD  
   - 10 AM: Sell 1 AMD  → 1st day-trade  
   - 10:30 AM: Buy 1 AMD  
   - 3 PM: Sell 1 AMD   → 2nd day-trade

4. **Scenario D: Sell Old, Then Buy & Sell New**  
   - 9 AM: Sell 1 AMD (shares held overnight)  
   - 10 AM: Buy 1 AMD  
   - 4 PM: Sell 1 AMD   → 1st day-trade

---

## 5. Rolling 5-Day Count & Your Block

Alpaca tallies how many day-trades you’ve done over the **last five** business days.

| Day | # of Day-Trades |
|-----|-----------------|
| Mon | 1               |
| Tue | 0               |
| Wed | 1               |
| Thu | 1               |
| Fri | — (today)       |  

> If you attempt another round-trip today (Fri), it would be your 4th in the 5-day window → **blocked**.

---

### 📝 Key Takeaways

- **Buys by themselves are “free.”** Pile on as many buys as you like.  
- **Only selling** the shares you bought **today** completes a round-trip and counts as a day-trade.  
- After **3** round-trips in any **5** business days (with <\$25 000 equity), Alpaca will reject further exits until one of your prior day-trades drops off the 5-day window.
